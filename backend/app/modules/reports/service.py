# app/modules/reports/service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import datetime
from fastapi.responses import StreamingResponse
import json
import traceback
import logging
from typing import Optional, Dict, Any

from app.db.models import Report, User, Subscription
from app.core.audit import log_action
from app.core.config import settings
from app.modules.reports.ai_engine import generate_life_signify_report
from app.modules.reports.pdf_engine import generate_report_pdf
from app.modules.reports.blueprint import (
    get_tier_section_blueprint,
    get_all_tier_section_blueprints,
)

# Setup logging
logger = logging.getLogger(__name__)

# =====================================================
# PLAN LIMITS
# =====================================================

PLAN_LIMITS = {
    "basic": 1,
    "pro": 5,
    "premium": 50,
    "enterprise": 200,
}

PLAN_NAMES = {
    "basic": "Basic Edition",
    "pro": "Professional Edition",
    "premium": "Premium Edition",
    "enterprise": "Enterprise Edition",
}


def _normalize_plan_name(plan_name: Optional[str]) -> str:
    plan = (plan_name or "").strip().lower()
    aliases = {
        "professional": "pro",
        "pro": "pro",
        "basic": "basic",
        "premium": "premium",
        "enterprise": "enterprise",
    }
    return aliases.get(plan, "basic")

def get_report_blueprint(plan_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Return section blueprint for a specific tier or all tiers.
    """
    if plan_name:
        normalized = _normalize_plan_name(plan_name)
        return get_tier_section_blueprint(normalized)

    blueprints = get_all_tier_section_blueprints()
    return {
        "tiers": blueprints,
        "total_defined_sections": max(
            blueprint.get("section_count", 0) for blueprint in blueprints.values()
        ),
    }

# =====================================================
# REPORT ENRICHMENT LAYER
# =====================================================

def enrich_report_content(report_content: dict, plan_name: str = "basic") -> dict:
    """
    Ensures the report always returns a complete schema with plan-specific content.
    Prevents null sections in API responses and PDF generation.
    """
    report_content = report_content or {}
    plan_name = _normalize_plan_name(plan_name)
    
    # Add metadata if missing
    if "meta" not in report_content:
        report_content["meta"] = {
            "plan_tier": plan_name,
            "generated_at": datetime.utcnow().isoformat(),
            "engine_version": settings.ENGINE_VERSION,
            "report_version": "6.0"
        }

    # Attach section blueprint so frontend/export layers can inspect tier coverage.
    report_content["report_blueprint"] = get_tier_section_blueprint(plan_name)
    report_content["meta"]["section_count"] = report_content["report_blueprint"]["section_count"]
    report_content["meta"]["blueprint_version"] = "2026-03-v2"

    
    # Executive Brief - Core summary
    report_content.setdefault(
        "executive_brief",
        {
            "summary": "आपके numerology indicators adaptive personality और leadership potential दिखाते हैं। वर्तमान pattern वित्तीय अनुशासन और emotional regulation में सुधार की दिशा बताता है।",
            "key_strength": "रणनीतिक सोच, adaptability, और vision-driven execution.",
            "key_risk": "Stress phase में financial discipline और emotional consistency में उतार-चढ़ाव।",
            "strategic_focus": "Structured planning और disciplined execution के साथ sustainable scaling पर फोकस रखें।"
        },
    )
    
    # Core Metrics - Always present for PDF dashboard
    report_content.setdefault(
        "core_metrics",
        {
            "risk_band": "Correctable",
            "confidence_score": 75,
            "data_completeness_score": 70,
            "karma_pressure_index": 50,
            "life_stability_index": 50,
            "dharma_alignment_score": 50,
            "emotional_regulation_index": 50,
            "financial_discipline_index": 50
        }
    )
    
    # Analysis Sections - Detailed behavioral analysis
    report_content.setdefault(
        "analysis_sections",
        {
            "career_analysis": "आपका numerology pattern leadership और ownership-oriented environments को support करता है। Life Path energy adaptability और innovation को drive करती है।",
            "decision_profile": "Decision clarity मध्यम है; pressure के समय structured decision framework अपनाने की आवश्यकता है।",
            "emotional_analysis": "Emotional regulation मध्यम है; stress phase में impulsive decisions से बचने के लिए recovery protocol आवश्यक है।",
            "financial_analysis": "Financial discipline signal बताता है कि savings, budgeting, और investment habits को अधिक structured बनाना लाभकारी रहेगा।"
        },
    )
    
    # Business Block - For professional/enterprise plans
    if plan_name in ["pro", "premium", "enterprise"]:
        report_content.setdefault(
            "business_block",
            {
                "business_strength": "Your business vibration supports strategic positioning in service-oriented sectors.",
                "risk_factor": "Success hinges on aligning leadership vision with operational discipline.",
                "compatible_industries": ["consulting", "education", "global services"]
            }
        )
    
    # Growth Blueprint - Strategic roadmap
    report_content.setdefault(
        "growth_blueprint",
        {
            "phase_1": "Structured routine के माध्यम से emotional और financial decision framework stabilize करें।",
            "phase_2": "Measurable milestones के साथ scalable growth strategy deploy करें।",
            "phase_3": "Long-term strategy को leadership opportunities और impact roadmap से align करें।"
        },
    )
    
    # Strategic Guidance - Actionable advice
    report_content.setdefault(
        "strategic_guidance",
        {
            "short_term": "Immediate cash-flow stabilization और emotional resilience practices पर फोकस करें।",
            "mid_term": "Operations restructure करके sustainable growth के लिए scalable systems बनाएं।",
            "long_term": "Aligned partnerships के साथ compatible industries में structured scaling करें।"
        },
    )
    
    # Numerology Core - Essential for all plans
    report_content.setdefault(
        "numerology_core",
        {
            "pythagorean": {
                "life_path_number": 5,
                "destiny_number": 11,
                "expression_number": 11
            },
            "chaldean": {
                "name_number": 3
            },
            "email_analysis": {
                "email_number": 3
            },
            "name_correction": {
                "suggestion": "Name vibration is stable.",
                "current_number": 3
            }
        }
    )
    
    # Loshu Grid - Essential for visualization
    if "loshu_grid" not in report_content.get("numerology_core", {}):
        if "numerology_core" not in report_content:
            report_content["numerology_core"] = {}
        report_content["numerology_core"]["loshu_grid"] = {
            "grid_counts": {
                "1": 1, "2": 1, "3": 1, "4": 1, "5": 1, 
                "6": 1, "7": 1, "8": 1, "9": 1
            },
            "missing_numbers": []
        }
    
    # Archetype - Identity profile
    report_content.setdefault(
        "numerology_archetype",
        {
            "archetype_name": "Strategic Adaptive Explorer",
            "core_archetype": "Adaptive Explorer",
            "behavior_style": "Adaptive Thinker",
            "description": "Dynamic, curious, and freedom-seeking. These individuals evolve through new experiences and intellectual exploration.",
            "interpretation": "This profile combines strategic traits with adaptive decision-making patterns."
        }
    )
    
    # Compatibility - For premium plans
    if plan_name in ["premium", "enterprise"]:
        report_content.setdefault(
            "compatibility_block",
            {
                "compatible_numbers": [3, 5, 9, 11],
                "challenging_numbers": [4, 6, 7, 8],
                "relationship_guidance": "Maintain relationships with compatible numbers for synergy."
            }
        )
    
    # Lifestyle Remedies - Daily practices
    report_content.setdefault(
        "lifestyle_remedies",
        {
            "meditation": "Practice 10 minutes of focused breathing daily.",
            "daily_routine": "Maintain disciplined schedule with morning sunlight exposure.",
            "color_alignment": "Use Green tones in clothing or workspace.",
            "bracelet_suggestion": "Wear colors aligned with your ruling number."
        }
    )
    
    # Mobile Remedies - Digital alignment
    report_content.setdefault(
        "mobile_remedies",
        {
            "whatsapp_dp": "Use a calm professional image reflecting clarity.",
            "mobile_wallpaper": "Use geometric or sacred symbol background.",
            "charging_direction": "Place phone facing East or North while charging.",
            "mobile_cover_color": "Green",
            "mobile_usage_timing": "Avoid heavy decisions late at night."
        }
    )
    
    # Vedic Remedies - Spiritual guidance
    if plan_name in ["premium", "enterprise"]:
        report_content.setdefault(
            "vedic_remedies",
            {
                "deity": "Budh (Mercury)",
                "mantra_sanskrit": "ॐ बुं बुधाय नमः",
                "mantra_pronunciation": "Om Bum Budhaya Namaha",
                "practice_guideline": "Chant 108 times every morning for 21 days.",
                "recommended_donation": "Donate green vegetables"
            }
        )
    
    # Radar Chart Data - For visualization
    metrics = report_content.get("core_metrics", {})
    report_content.setdefault(
        "radar_chart_data",
        {
            "Life Stability": metrics.get("life_stability_index", 50),
            "Decision Clarity": metrics.get("confidence_score", 75),
            "Dharma Alignment": metrics.get("dharma_alignment_score", 50),
            "Emotional Regulation": metrics.get("emotional_regulation_index", 50),
            "Financial Discipline": metrics.get("financial_discipline_index", 50)
        }
    )
    
    # Disclaimer - Always present
    report_content.setdefault(
        "disclaimer",
        {
            "note": "Insights are probabilistic and strategic, not deterministic predictions.",
            "framework": "Tiered Numerology Intelligence System",
            "confidence_score": report_content.get("core_metrics", {}).get("confidence_score", 75)
        }
    )
    
    # Correction Block - For name/email corrections
    report_content.setdefault("correction_block", {})
    
    return report_content


# =====================================================
# RADAR DATA
# =====================================================

def get_radar_data(db: Session, current_user: User, report_id: int) -> Dict[str, int]:
    """
    Extract radar chart data from report metrics
    """
    report = get_report(db, current_user, report_id)
    content = report.content or {}
    metrics = content.get("core_metrics", {})
    
    return {
        "Life Stability": metrics.get("life_stability_index", 50),
        "Decision Clarity": metrics.get("confidence_score", 50),
        "Dharma Alignment": metrics.get("dharma_alignment_score", 50),
        "Emotional Regulation": metrics.get("emotional_regulation_index", 50),
        "Financial Discipline": metrics.get("financial_discipline_index", 50),
        "Karma Pressure": metrics.get("karma_pressure_index", 50),
    }


# =====================================================
# SUBSCRIPTION VALIDATION
# =====================================================

def _validate_and_lock_subscription(db: Session, current_user: User) -> Subscription:
    """
    Validate subscription and lock row for update to prevent race conditions
    """
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.tenant_id == current_user.tenant_id,
            Subscription.is_active.is_(True),
        )
        .with_for_update()
        .first()
    )

    if not subscription:
        logger.warning(f"No active subscription for tenant {current_user.tenant_id}")
        raise HTTPException(
            status_code=403, 
            detail="Active subscription required to generate reports"
        )

    if subscription.end_date and subscription.end_date < datetime.utcnow():
        subscription.is_active = False
        db.commit()
        logger.info(f"Subscription expired for tenant {current_user.tenant_id}")
        raise HTTPException(
            status_code=403, 
            detail="Subscription expired. Please renew to continue."
        )

    return subscription


# =====================================================
# CREATE MANUAL REPORT
# =====================================================

def create_report(
    db: Session, 
    current_user: User, 
    title: str,
    content: dict,
    plan_override: Optional[str] = None
) -> Report:
    """
    Create a manually crafted report
    """
    plan = _normalize_plan_name(plan_override or "pro")
    
    # Enrich content with defaults
    enriched_content = enrich_report_content(content, plan)
    
    report = Report(
        title=title,
        content=enriched_content,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        engine_version="manual",
        confidence_score=enriched_content.get("core_metrics", {}).get("confidence_score", 75),
    )

    try:
        db.add(report)
        db.commit()
        db.refresh(report)

        log_action(
            db=db,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="REPORT_CREATED",
            details={"report_id": report.id, "type": "manual"},
        )
        
        logger.info(f"Manual report created: {report.id} for user {current_user.id}")
        return report

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Manual report creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Manual report creation failed")


# =====================================================
# UPDATE REPORT
# =====================================================

def update_report(
    db: Session, 
    current_user: User, 
    report_id: int, 
    title: Optional[str],
    content: Optional[dict]
) -> Report:
    """
    Update an existing report
    """
    report = get_report(db, current_user, report_id)

    try:
        if title is not None:
            report.title = title
        if content is not None:
            report.content = content

        report.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(report)

        log_action(
            db=db,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="REPORT_UPDATED",
            details={"report_id": report.id},
        )
        
        logger.info(f"Report updated: {report_id}")
        return report

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Report update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Report update failed")


# =====================================================
# SOFT DELETE REPORT
# =====================================================

def soft_delete_report(db: Session, current_user: User, report_id: int) -> Dict[str, str]:
    """
    Soft delete a report (mark as deleted)
    """
    report = get_report(db, current_user, report_id)

    report.is_deleted = True
    db.commit()
    
    logger.info(f"Report soft deleted: {report_id}")
    return {"message": "Report moved to trash"}


# =====================================================
# RESTORE REPORT
# =====================================================

def restore_report(db: Session, current_user: User, report_id: int) -> Dict[str, str]:
    """
    Restore a soft-deleted report
    """
    report = (
        db.query(Report)
        .filter(
            Report.id == report_id,
            Report.tenant_id == current_user.tenant_id,
            Report.is_deleted.is_(True),
        )
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Deleted report not found")


    if not current_user.is_admin and report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only access your own reports")
    report.is_deleted = False
    db.commit()
    
    logger.info(f"Report restored: {report_id}")
    return {"message": "Report restored successfully"}


# =====================================================
# HARD DELETE REPORT
# =====================================================

def hard_delete_report(db: Session, current_user: User, report_id: int) -> Dict[str, str]:
    """
    Permanently delete a report (admin only)
    """
    report = (
        db.query(Report)
        .filter(
            Report.id == report_id,
            Report.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()
    
    logger.info(f"Report permanently deleted: {report_id}")
    return {"message": "Report permanently deleted"}


# =====================================================
# GENERATE AI REPORT
# =====================================================

def generate_ai_report_service(
    db: Session, 
    current_user: User, 
    intake_data: dict
) -> Report:
    """
    Generate AI-powered numerology report with plan-based limits
    """
    try:
        # Validate subscription and lock for update
        subscription = _validate_and_lock_subscription(db, current_user)

        # Determine plan from the active subscription only
        plan_name = _normalize_plan_name(subscription.plan_name or "basic")

        if plan_name not in PLAN_LIMITS:
            logger.error(f"Invalid plan name: {plan_name}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid plan: {plan_name}"
            )

        # Check report limits
        limit = PLAN_LIMITS[plan_name]
        used = subscription.reports_used or 0

        if used >= limit:
            logger.warning(
                f"Report limit reached for tenant {current_user.tenant_id}: "
                f"{used}/{limit}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Monthly report limit ({limit}) reached. Upgrade required.",
            )

        # Normalize intake data for AI
        normalized_data = {
            "identity": intake_data.get("identity", {}),
            "birth_details": intake_data.get("birth_details", {}),
            "focus": intake_data.get("focus", {}),
            "financial": intake_data.get("financial", {}),
            "career": intake_data.get("career", {}),
            "emotional": intake_data.get("emotional", {}),
            "life_events": intake_data.get("life_events", {}),
            "calibration": intake_data.get("calibration", {}),
            "contact": intake_data.get("contact", {}),
            "preferences": intake_data.get("preferences", {}),
            "current_problem": intake_data.get("current_problem", ""),
        }

        # Generate AI content
        logger.info(f"Generating AI report for user {current_user.id}, plan: {plan_name}")
        ai_output = generate_life_signify_report(
            request_data=normalized_data,
            plan_name=plan_name,
        )

        # Parse if string
        if isinstance(ai_output, str):
            try:
                ai_output = json.loads(ai_output)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI output as JSON: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail="AI response parsing failed"
                )

        # Enrich with defaults and ensure complete schema
        enriched_content = enrich_report_content(ai_output, plan_name)

        # Extract confidence score
        confidence_score = (
            enriched_content.get("disclaimer", {}).get("confidence_score") or
            enriched_content.get("core_metrics", {}).get("confidence_score") or
            80
        )

        # Create report record
        report = Report(
            title=f"Life Signify NumAI Report ({PLAN_NAMES.get(plan_name, plan_name.title())})",
            content=enriched_content,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            engine_version=settings.ENGINE_VERSION,
            confidence_score=confidence_score,
        )

        db.add(report)
        
        # Increment usage counter
        subscription.reports_used = used + 1
        
        db.commit()
        db.refresh(report)

        log_action(
            db=db,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="REPORT_GENERATED",
            details={
                "report_id": report.id,
                "plan": plan_name,
                "confidence": confidence_score
            },
        )

        logger.info(
            f"Report generated successfully: {report.id} "
            f"(used {used+1}/{limit} for plan {plan_name})"
        )
        
        return report

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"AI report generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}",
        )


# =====================================================
# GET ALL REPORTS
# =====================================================

def get_reports(
    db: Session, 
    current_user: User, 
    skip: int = 0, 
    limit: int = 100,
    include_deleted: bool = False
) -> list[Report]:
    """
    Get all reports for current user with pagination
    """
    query = db.query(Report).filter(
        Report.tenant_id == current_user.tenant_id
    )

    if not current_user.is_admin:
        query = query.filter(Report.user_id == current_user.id)
    
    if not include_deleted:
        query = query.filter(Report.is_deleted.is_(False))
    
    return (
        query.order_by(Report.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# =====================================================
# GET SINGLE REPORT
# =====================================================

def get_report(
    db: Session, 
    current_user: User, 
    report_id: int,
    include_deleted: bool = False
) -> Report:
    """
    Get a single report by ID
    """
    query = db.query(Report).filter(
        Report.id == report_id,
        Report.tenant_id == current_user.tenant_id,
    )
    
    if not include_deleted:
        query = query.filter(Report.is_deleted.is_(False))
    
    report = query.first()

    if not report:
        raise HTTPException(
            status_code=404, 
            detail="Report not found"
        )


    if not current_user.is_admin and report.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own reports",
        )
    return report


# =====================================================
# EXPORT PDF - OPTIMIZED VERSION
# =====================================================

def export_report_pdf(
    db: Session, 
    current_user: User, 
    report_id: int,
    watermark: bool = False
) -> StreamingResponse:
    """
    Export a report as PDF with premium formatting
    
    Args:
        db: Database session
        current_user: Authenticated user
        report_id: Report ID to export
        watermark: Force watermark (for basic plan previews)
    
    Returns:
        StreamingResponse with PDF attachment
    """
    # Get report with access check
    report = get_report(db, current_user, report_id)
    
    if not report.content:
        logger.error(f"Report {report_id} has no content")
        raise HTTPException(
            status_code=404, 
            detail="Report content not found"
        )
    
    # Log export attempt
    logger.info(f"Exporting report {report_id} to PDF for user {current_user.id}")
    
    try:
        # Generate PDF from content
        pdf_buffer = generate_report_pdf(report.content, watermark=watermark)
        
        # Determine filename
        plan_tier = report.content.get("meta", {}).get("plan_tier", "standard")
        filename = f"NumAI_Strategic_Brief_{report_id}_{plan_tier}.pdf"
        
        # Return streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf",
                "Cache-Control": "no-cache",
            }
        )
        
    except Exception as e:
        logger.error(f"PDF generation failed for report {report_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="PDF generation failed. Please try again or contact support."
        )


# =====================================================
# GET REPORT METRICS
# =====================================================

def get_report_metrics(
    db: Session, 
    current_user: User
) -> Dict[str, Any]:
    """
    Get usage metrics for reports
    """
    total = db.query(Report).filter(
        Report.tenant_id == current_user.tenant_id,
        Report.is_deleted.is_(False)
    ).count()
    
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == current_user.tenant_id,
        Subscription.is_active.is_(True)
    ).first()
    
    if subscription:
        used = subscription.reports_used or 0
        limit = PLAN_LIMITS.get(_normalize_plan_name(subscription.plan_name), 0)
        remaining = max(0, limit - used)
    else:
        used = 0
        limit = 0
        remaining = 0
    
    return {
        "total_reports": total,
        "subscription_plan": subscription.plan_name if subscription else "none",
        "reports_used_this_month": used,
        "monthly_limit": limit,
        "reports_remaining": remaining
    }


# =====================================================
# BULK DELETE REPORTS
# =====================================================

def bulk_delete_reports(
    db: Session,
    current_user: User,
    report_ids: list[int],
    permanent: bool = False
) -> Dict[str, Any]:
    """
    Bulk delete multiple reports
    """
    reports = db.query(Report).filter(
        Report.id.in_(report_ids),
        Report.tenant_id == current_user.tenant_id
    ).all()
    
    found_ids = [r.id for r in reports]
    not_found = set(report_ids) - set(found_ids)
    
    if permanent:
        # Hard delete
        for report in reports:
            db.delete(report)
        action = "permanently deleted"
    else:
        # Soft delete
        for report in reports:
            report.is_deleted = True
        action = "moved to trash"
    
    db.commit()
    
    logger.info(f"Bulk {action} {len(reports)} reports for user {current_user.id}")
    
    return {
        "message": f"Successfully {action} {len(reports)} reports",
        "processed_ids": found_ids,
        "not_found_ids": list(not_found)
    }















