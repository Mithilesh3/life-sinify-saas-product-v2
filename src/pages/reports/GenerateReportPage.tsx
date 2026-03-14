import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import API from "../../services/api";
import DashboardCard from "../../components/ui/DashboardCard";
import { useAuth } from "../../context/AuthContext";
import { useUsage } from "../../context/UsageContext";
import type { Report } from "../../types/report";

import StepIdentity from "../../components/reports/steps/StepIdentity";
import StepBirthDetails from "../../components/reports/steps/StepBirthDetails";
import StepFocus from "../../components/reports/steps/StepFocus";
import StepFinancial from "../../components/reports/steps/StepFinancial";
import StepEmotional from "../../components/reports/steps/StepEmotional";
import StepBusiness from "../../components/reports/steps/StepBusiness";
import StepHealth from "../../components/reports/steps/StepHealth";
import StepCalibration from "../../components/reports/steps/StepCalibration";
import StepReview from "../../components/reports/steps/StepReview";

type FocusValue =
  | ""
  | "finance_debt"
  | "career_growth"
  | "relationship"
  | "health_stability"
  | "emotional_confusion"
  | "business_decision"
  | "general_alignment";

type OptionalNumber = number | "";

interface FormState {
  identity: {
    full_name: string;
    gender: "" | "male" | "female" | "other";
    country_of_residence: string;
    email: string;
    partner_name: string;
    business_name: string;
  };
  birth_details: {
    date_of_birth: string;
    time_of_birth: string;
    birthplace_city: string;
    birthplace_country: string;
  };
  focus: {
    life_focus: FocusValue;
  };
  financial: {
    monthly_income: OptionalNumber;
    savings_ratio: OptionalNumber;
    debt_ratio: OptionalNumber;
    risk_tolerance: "" | "low" | "moderate" | "high";
  };
  emotional: {
    anxiety_level: OptionalNumber;
    decision_confusion: OptionalNumber;
    impulse_control: OptionalNumber;
    emotional_stability: OptionalNumber;
  };
  business_history: {
    major_investments: OptionalNumber;
    major_losses: OptionalNumber;
    risk_mistakes_count: OptionalNumber;
  };
  health: {
    sleep_hours: OptionalNumber;
    alcohol: "" | "true" | "false";
    smoking: "" | "true" | "false";
    exercise_frequency_per_week: OptionalNumber;
    food_pattern: "" | "veg" | "non_veg" | "mixed";
  };
  calibration: {
    stress_response: "" | "withdraw" | "impulsive" | "overthink" | "take_control";
    money_decision_style: "" | "emotional" | "calculated" | "risky" | "avoidant";
    biggest_weakness: "" | "discipline" | "patience" | "confidence" | "focus";
    life_preference: "" | "stability" | "growth" | "recognition" | "freedom";
    decision_style: "" | "fast" | "research" | "advice" | "emotional";
  };
  current_problem: string;
}

const initialState: FormState = {
  identity: {
    full_name: "",
    gender: "",
    country_of_residence: "",
    email: "",
    partner_name: "",
    business_name: "",
  },
  birth_details: {
    date_of_birth: "",
    time_of_birth: "",
    birthplace_city: "",
    birthplace_country: "",
  },
  focus: {
    life_focus: "",
  },
  financial: {
    monthly_income: "",
    savings_ratio: "",
    debt_ratio: "",
    risk_tolerance: "",
  },
  emotional: {
    anxiety_level: "",
    decision_confusion: "",
    impulse_control: "",
    emotional_stability: "",
  },
  business_history: {
    major_investments: "",
    major_losses: "",
    risk_mistakes_count: "",
  },
  health: {
    sleep_hours: "",
    alcohol: "",
    smoking: "",
    exercise_frequency_per_week: "",
    food_pattern: "",
  },
  calibration: {
    stress_response: "",
    money_decision_style: "",
    biggest_weakness: "",
    life_preference: "",
    decision_style: "",
  },
  current_problem: "",
};

export default function GenerateReportPage() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const { refreshUsage } = useUsage();
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormState>(initialState);

  const plan = user?.subscription?.plan_name?.toLowerCase() || "basic";

  const steps: Array<{ key: string; component: any }> = [
    { key: "identity", component: StepIdentity },
    { key: "birth_details", component: StepBirthDetails },
    { key: "focus", component: StepFocus },
  ];

  if (plan !== "basic") {
    steps.push(
      { key: "financial", component: StepFinancial },
      { key: "emotional", component: StepEmotional }
    );
  }

  if (plan === "enterprise") {
    steps.push(
      { key: "business_history", component: StepBusiness },
      { key: "health", component: StepHealth },
      { key: "calibration", component: StepCalibration }
    );
  }

  steps.push({ key: "review", component: StepReview });

  const totalSteps = steps.length;
  const currentStep = steps[Math.min(step - 1, totalSteps - 1)];
  const CurrentStepComponent = currentStep.component;

  const next = () => setStep((current) => Math.min(current + 1, totalSteps));
  const prev = () => setStep((current) => Math.max(current - 1, 1));

  const isEmptyValue = (value: unknown) => {
    if (value === "" || value === undefined || value === null) {
      return true;
    }

    if (Array.isArray(value)) {
      return value.length === 0;
    }

    return false;
  };

  const cleanObject = <T extends Record<string, unknown>>(obj: T): Partial<T> => {
    return Object.fromEntries(Object.entries(obj).filter(([, value]) => !isEmptyValue(value))) as Partial<T>;
  };

  const optionalSection = <T extends Record<string, unknown>>(obj: T) => {
    const cleaned = cleanObject(obj);
    return Object.keys(cleaned).length > 0 ? cleaned : undefined;
  };

  const parseBoolean = (value: "" | "true" | "false") => {
    if (value === "") return undefined;
    return value === "true";
  };

  const handleSubmit = async () => {
    if (
      !formData.identity.full_name.trim() ||
      !formData.identity.country_of_residence.trim() ||
      !formData.birth_details.date_of_birth ||
      !formData.birth_details.birthplace_city.trim() ||
      !formData.birth_details.birthplace_country.trim() ||
      !formData.focus.life_focus
    ) {
      toast.error("Please fill all required fields.");
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        identity: cleanObject({
          ...formData.identity,
          date_of_birth: formData.birth_details.date_of_birth,
        }),
        birth_details: cleanObject(formData.birth_details),
        focus: cleanObject(formData.focus),
        current_problem: formData.current_problem.trim() || undefined,
        financial: optionalSection(formData.financial),
        emotional: optionalSection(formData.emotional),
        business_history: optionalSection(formData.business_history),
        health: optionalSection({
          ...formData.health,
          alcohol: parseBoolean(formData.health.alcohol),
          smoking: parseBoolean(formData.health.smoking),
        }),
        calibration: optionalSection(formData.calibration),
      };

      const response = await API.post<Report>("/reports/generate-ai-report", payload);

      await Promise.all([refreshUser(), refreshUsage()]);

      toast.success("Report generated successfully");
      navigate(`/reports/${response.data.id}`);
    } catch (error: any) {
      if (error?.response?.status === 422) {
        const details = error.response.data?.detail;

        if (Array.isArray(details)) {
          const message = details
            .map((item: { loc?: Array<string | number>; msg?: string }) => `${item.loc?.join(" -> ") ?? "field"}: ${item.msg ?? "Invalid value"}`)
            .join("\n");

          toast.error(message);
        } else {
          toast.error("Invalid input data.");
        }
      } else if (error?.response?.status === 403) {
        toast.error(error?.response?.data?.detail || "Your subscription does not allow this.");
      } else {
        toast.error("Something went wrong.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="premium-page mx-auto max-w-[980px]">
      <DashboardCard hover={false}>
        <p className="sidebar-label text-slate-400">Report Generator</p>
        <h1 className="page-heading">Generate Report</h1>
        <p className="page-copy">
          This form uses the backend request schema and valid enum values while keeping spacing, typography, and actions aligned with the rest of the dashboard.
        </p>

        <div className="mt-6 h-2 overflow-hidden rounded-full bg-slate-950/80">
          <div
            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>

        <p className="type-body mt-4">
          Step {step} of {totalSteps}. Current plan: {plan.toUpperCase()}.
        </p>
      </DashboardCard>

      <DashboardCard compact title={currentStep.key.replace(/_/g, " ")} description="Complete the required fields and move through the guided report flow.">
        <CurrentStepComponent
          formData={formData}
          setFormData={setFormData}
          next={next}
          prev={prev}
          submit={handleSubmit}
          plan={plan}
          submitting={submitting}
        />
      </DashboardCard>
    </div>
  );
}