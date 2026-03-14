import { motion } from "framer-motion";
import type { ReactNode } from "react";

const services = [
  "Name Numerology Correction",
  "Business Name Numerology",
  "Mobile Number Numerology",
  "Vehicle Number Numerology",
  "House Number Numerology",
  "Signature Numerology",
  "Birth Chart Analysis",
  "Kundli Matching",
  "Career Prediction",
  "Love and Relationship Prediction",
  "Health Astrology",
  "Wealth Prediction",
];

const rituals = [
  "Marriage Muhurat",
  "Griha Pravesh Muhurat",
  "Naamkaran Muhurat",
  "Mundan Muhurat",
  "Car/Bike Muhurat",
  "Bhoomi Pujan Muhurat",
  "Business Opening Muhurat",
  "Maha Mrityunjaya Jaap",
  "Rudra Abhishek",
  "Navgraha Shanti",
  "Pitru Dosh Puja",
  "Kaal Sarp Dosh Puja",
  "Manglik Dosh Puja",
];

const products = [
  "Rudraksha",
  "Rudraksha Mala",
  "Rudraksha Bracelet",
  "Blue Sapphire (Neelam)",
  "Yellow Sapphire (Pukhraj)",
  "Emerald (Panna)",
  "Ruby (Manik)",
  "Shree Yantra",
  "Navgraha Yantra",
  "Money Magnet Bracelet",
];

const trustBadges = ["Private and Confidential", "Verified Astrologers", "Secure Payments"];

const aiTools = [
  "Live Astrologer Chat",
  "AI Numerology Report Generator",
  "Compatibility Calculator",
  "Lucky Number Generator",
  "Name Correction Tool",
  "AI Birth Chart Reader",
];

const socialLinks = [
  { label: "Facebook", href: "https://www.facebook.com/lifesignify" },
  { label: "Instagram", href: "https://www.instagram.com/lifesignify/" },
  { label: "YouTube", href: "https://www.youtube.com/@LifeSignify" },
] as const;

function FooterLink({ label }: { label: string }) {
  return (
    <motion.a
      whileHover={{ x: 3 }}
      whileTap={{ scale: 0.99 }}
      href="#"
      onClick={(event) => event.preventDefault()}
      className="footer-link"
    >
      {label}
    </motion.a>
  );
}

function SocialIcon({
  label,
  href,
  children,
}: {
  label: string;
  href: string;
  children: ReactNode;
}) {
  return (
    <motion.a
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.96 }}
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="footer-social"
      aria-label={label}
      title={label}
    >
      {children}
    </motion.a>
  );
}

export default function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className="site-footer"
    >
      <div className="footer-cosmic-overlay" aria-hidden>
        <span className="footer-orbit footer-orbit-1" />
        <span className="footer-orbit footer-orbit-2" />
        <span className="footer-orbit footer-orbit-3" />
        <span className="footer-num footer-num-3">3</span>
        <span className="footer-num footer-num-7">7</span>
        <span className="footer-num footer-num-9">9</span>
        <span className="footer-num footer-num-11">11</span>
        <span className="footer-num footer-num-22">22</span>
        <span className="footer-num footer-num-33">33</span>
        <span className="footer-star footer-star-1" />
        <span className="footer-star footer-star-2" />
        <span className="footer-star footer-star-3" />
        <span className="footer-star footer-star-4" />
      </div>

      <div className="site-footer-inner">
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.35 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          className="footer-about"
        >
          <h3 className="footer-about-title">About LifeSignify</h3>
          <p className="footer-about-copy">
            LifeSignify NumAI combines ancient Vedic wisdom with AI-powered numerology and astrology guidance to help people find clarity in life, relationships, career, and destiny.
          </p>
          <p className="footer-about-copy">
            From personalized reports to rituals, gemstones, and spiritual products, we provide a complete spiritual ecosystem for seekers across India.
          </p>
        </motion.section>

        <div className="site-footer-grid">
          <motion.section className="footer-column" whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
            <h4 className="footer-title">Vedic Intelligence</h4>
            <div className="footer-links">
              {services.map((item) => (
                <FooterLink key={item} label={item} />
              ))}
            </div>
          </motion.section>

          <motion.section className="footer-column" whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
            <h4 className="footer-title">Muhurat and Rituals Intelligence</h4>
            <div className="footer-links">
              {rituals.map((item) => (
                <FooterLink key={item} label={item} />
              ))}
            </div>
          </motion.section>

          <motion.section className="footer-column" whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
            <h4 className="footer-title">Spiritual Store Intelligence</h4>
            <div className="footer-links">
              {products.map((item) => (
                <FooterLink key={item} label={item} />
              ))}
            </div>
          </motion.section>

          <motion.section className="footer-column" whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
            <h4 className="footer-title">Contact and Trust</h4>
            <p className="footer-copy">We are available 24x7 on chat support</p>
            <a className="footer-email" href="mailto:support@lifesignify.ai">
              support@lifesignify.ai
            </a>

            <div className="footer-social-section">
              <p className="footer-tools-title">Follow LifeSignify</p>
              <div className="footer-social-row">
                <SocialIcon label={socialLinks[0].label} href={socialLinks[0].href}>
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M13.5 9H16V6h-2.5C10.9 6 9 7.9 9 10.5V13H7v3h2v5h3v-5h2.4l.6-3H12v-2.5c0-.8.7-1.5 1.5-1.5Z" />
                  </svg>
                </SocialIcon>
                <SocialIcon label={socialLinks[1].label} href={socialLinks[1].href}>
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M7.5 3h9A4.5 4.5 0 0 1 21 7.5v9a4.5 4.5 0 0 1-4.5 4.5h-9A4.5 4.5 0 0 1 3 16.5v-9A4.5 4.5 0 0 1 7.5 3Zm0 2A2.5 2.5 0 0 0 5 7.5v9A2.5 2.5 0 0 0 7.5 19h9a2.5 2.5 0 0 0 2.5-2.5v-9A2.5 2.5 0 0 0 16.5 5h-9Zm10.25 1.5a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0ZM12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8Zm0 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z" />
                  </svg>
                </SocialIcon>
                <SocialIcon label={socialLinks[2].label} href={socialLinks[2].href}>
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M21.6 8.6a2.7 2.7 0 0 0-1.9-1.9C18 6.2 12 6.2 12 6.2s-6 0-7.7.5a2.7 2.7 0 0 0-1.9 1.9C2 10.3 2 12 2 12s0 1.7.4 3.4a2.7 2.7 0 0 0 1.9 1.9c1.7.5 7.7.5 7.7.5s6 0 7.7-.5a2.7 2.7 0 0 0 1.9-1.9c.4-1.7.4-3.4.4-3.4s0-1.7-.4-3.4ZM10 14.8V9.2L15 12l-5 2.8Z" />
                  </svg>
                </SocialIcon>
              </div>
            </div>

            <div className="footer-badges">
              {trustBadges.map((badge) => (
                <motion.span key={badge} whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} className="footer-badge">
                  {badge}
                </motion.span>
              ))}
            </div>

            <div className="footer-tools">
              <motion.h4
                whileHover={{ x: 2, scale: 1.01 }}
                transition={{ duration: 0.2 }}
                className="footer-title footer-tools-title"
              >
                AI Tools Intelligence
              </motion.h4>
              <div className="footer-links">
                {aiTools.map((tool) => (
                  <FooterLink key={tool} label={tool} />
                ))}
              </div>
            </div>
          </motion.section>
        </div>

        <div className="site-footer-bottom">© 2026 LifeSignify NumAI. All rights reserved.</div>
      </div>
    </motion.footer>
  );
}
