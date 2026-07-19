import React from "react";
import { Link } from "react-router-dom";
import { Mail, ShieldCheck } from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { RahafitLogo } from "../common/RahafitLogo";

export const PublicFooter: React.FC = () => {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = locale === "ar";

  return (
    <footer className="public-footer-container" dir={direction}>
      <div className="public-footer-inner-grid">
        {/* Brand & Description Column */}
        <div className="footer-col footer-col-brand">
          <Link to="/" aria-label="Rahafit Home">
            <RahafitLogo size="md" />
          </Link>
          <p className="footer-brand-desc mt-3 text-sm text-slate-400 max-w-sm">
            {copy.footerDescription ||
              (isRtl
                ? "تمارين مخصصة، تغذية متوازنة، وتوجيه آمن يراعي صحتك وسلامتك البدنية في كل خطوة."
                : "Intelligent training, adaptive nutrition, and safety-guided coaching for sustainable health.")}
          </p>
          <div className="footer-trust-badge mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <ShieldCheck size={14} />
            <span>{isRtl ? "بياناتك محمية ومحفوظة بخصوصية" : "Privacy & Safety First"}</span>
          </div>
        </div>

        {/* Quick Navigation Links Column */}
        <div className="footer-col">
          <h4 className="footer-heading">{isRtl ? "التنقل السريع" : "Quick Navigation"}</h4>
          <ul className="footer-links-list">
            <li>
              <Link to="/">{copy.navHome || (isRtl ? "الرئيسية" : "Home")}</Link>
            </li>
            <li>
              <Link to="/discover">{copy.navDiscover}</Link>
            </li>
            <li>
              <a href="#how-it-works">{copy.navHowItWorks}</a>
            </li>
            <li>
              <a href="#product-areas">{copy.navFeatures}</a>
            </li>
            <li>
              <a href="#safety-section">{copy.navSafety}</a>
            </li>
          </ul>
        </div>

        {/* Account Links Column */}
        <div className="footer-col">
          <h4 className="footer-heading">{isRtl ? "الحساب والدخول" : "Account & Access"}</h4>
          <ul className="footer-links-list">
            <li>
              <Link to="/login">{copy.navLogin}</Link>
            </li>
            <li>
              <Link to="/register">{copy.navRegister}</Link>
            </li>
          </ul>
        </div>

        {/* Contact Information Column */}
        <div className="footer-col">
          <h4 className="footer-heading">
            {copy.footerContactHeading || (isRtl ? "التواصل والدعم" : "Contact & Support")}
          </h4>
          <p className="text-sm text-slate-400 flex items-center gap-2">
            <Mail size={16} className="text-teal-400 shrink-0" />
            <span>
              {copy.footerContactNotice ||
                (isRtl ? "معلومات التواصل قريباً." : "Contact information coming soon.")}
            </span>
          </p>
        </div>
      </div>

      {/* Bottom Copyright Bar */}
      <div className="public-footer-bottom mt-10 pt-6 border-t border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
        <p>© {new Date().getFullYear()} Rahafit. All rights reserved.</p>
        <div className="footer-legal-links flex gap-4">
          <a href="#privacy" className="hover:text-slate-300">
            {isRtl ? "سياسة الخصوصية" : "Privacy Policy"}
          </a>
          <a href="#terms" className="hover:text-slate-300">
            {isRtl ? "الشروط والأحكام" : "Terms of Service"}
          </a>
        </div>
      </div>
    </footer>
  );
};
