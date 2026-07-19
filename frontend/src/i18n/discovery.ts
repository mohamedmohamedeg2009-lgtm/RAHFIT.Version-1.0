import type { Locale } from "../contexts/LocaleContext";

export const discoveryCopy: Record<Locale, Record<string, string>> = {
  en: {
    // Header & Nav
    navBrand: "Rahafit",
    navFeatures: "Features",
    navHowItWorks: "How it works",
    navSafety: "Safety & Privacy",
    navPricing: "Pricing",
    navLogin: "Sign in",
    navDiscover: "Explore Rahafit",
    navRegister: "Create account",

    // Hero Section Reference
    heroTrustBadge: "Safe, Intelligent & Privacy-First Athletic Training",
    landingHeroHeadline: "Start Your Journey with Rahafit",
    landingHeroSubheading:
      "Rahafit connects athletic planning, nutrition tracking, recovery signals, and intelligent guidance that respects your goals and condition in one seamless experience.",
    landingHeroPrimaryCta: "Create your account",
    landingHeroSecondaryCta: "Explore features",
    landingHeroTertiaryCta: "Skip to sign in",
    heroHeading: "Start Your Journey with Rahafit",
    heroSubheading:
      "Rahafit connects your fitness programming, nutrition tracking, recovery insights, and safety-aware AI guidance into one seamless experience.",
    heroPrimaryCta: "Create account",
    heroSecondaryCta: "Explore features",

    // How Rahafit Works Section
    howItWorksEyebrow: "HOW IT WORKS",
    howItWorksHeading: "Your Journey with Rahafit in Four Steps",
    howItWorksSubheading:
      "From account creation to daily tracking, every step is designed to be clear, safe, and personalized for you.",
    step1Title: "Create Your Account",
    step1Desc: "Get started in minutes and securely log your core details.",
    step2Title: "Set Your Goals & Condition",
    step2Desc: "Complete the smart assessment to outline your targets and readiness level.",
    step3Title: "Get a Personalized Experience",
    step3Desc: "Rahafit relies on your data to provide appropriate and safe guidance.",
    step4Title: "Track Your Progress Daily",
    step4Desc: "Review workouts, nutrition, readiness, and progress from a single dashboard.",
    howItWorksPrimaryCta: "Start your journey",
    howItWorksSecondaryCta: "Explore features",

    // Core Areas & Features Section
    featuresEyebrow: "CORE FEATURES",
    featuresHeading: "Everything You Need for Smarter, Safer Training",
    featuresSubheading:
      "From personalized workouts to smart assessment and safe AI guidance, Rahafit unifies essential tools in one seamless experience.",
    featureWorkoutBadge: "Core Feature",
    featureWorkoutTitle: "Intelligent Workout Guidance",
    featureWorkoutDesc:
      "Deterministic workout programs adapting to your fitness level and equipment, with exercise substitutions and live safety alerts.",
    featureWorkoutPoint1: "Customizable workout plan",
    featureWorkoutPoint2: "Pain & rest timer tracking",
    featureWorkoutPoint3: "Safe exercise substitutions",
    featureWorkoutCta: "Explore Workout",

    featureAssessmentBadge: "Safe Assessment",
    featureAssessmentTitle: "Smart Assessment & Health Declaration",
    featureAssessmentDesc:
      "Capturing physical limitations and athletic history to build a safe health profile.",

    featureAiCoachBadge: "Intelligent & Safe Guidance",
    featureAiCoachTitle: "AI Coach & Safety Guidance",
    featureAiCoachDesc:
      "Real-time safety-bounded fitness guidance. Advice is athletic lifestyle support, not medical diagnosis.",
    featureAiChip1: "Workouts",
    featureAiChip2: "Nutrition",
    featureAiChip3: "Recovery",
    featureAiChip4: "Progress",
    featureAiDisclaimer: "AI recommendations provide fitness guidance and do not replace professional medical advice.",

    // Dashboard Preview Section
    previewEyebrow: "PRODUCT PREVIEW",
    previewHeading: "An Intelligent Dashboard Putting Core Metrics Front & Center",
    previewSubheading:
      "Real-time tracking for readiness, workouts, nutrition, and AI coaching insights in a single view.",
    previewBadgeReadiness: "Readiness 88%",
    previewBadgeWorkout: "Workout Ready",
    previewBadgeNutrition: "Macro Targets",
    previewInsightText: "Recovery signals optimal — proceed with today's planned upper body strength workout.",

    // AI Coach Showcase Section
    coachEyebrow: "AI COACH SHOWCASE",
    coachHeading: "Safety-Bounded Athletic Consultation",
    coachSubheading:
      "Get personalized training guidance respecting your health declaration and readiness.",
    coachSamplePrompt: "How should I train today if I feel slight fatigue?",
    coachSampleReply:
      "Based on your daily health check-in and readiness score (88%), workout intensity was adjusted with a 15% weight reduction to protect your muscles and ensure safe recovery.",

    // Honest Quality Metrics Section
    trustMetric1Title: "Deterministic Safety Rules Engine",
    trustMetric1Desc: "Enforcing exercise substitutions and rest when pain is logged.",
    trustMetric2Title: "Bilingual Arabic & English Support",
    trustMetric2Desc: "Complete localized experience with native RTL/LTR layout.",
    trustMetric3Title: "Owner-Scoped Encrypted Privacy",
    trustMetric3Desc: "Strict authentication and zero data sharing across accounts.",
    trustMetric4Title: "Verified Technical Foundation",
    trustMetric4Desc: "Tested across 530+ backend pytest test cases & 130+ frontend tests.",

    // Platform Scope Pillars
    scopeEyebrow: "PLATFORM SCOPE",
    scopeHeading: "Five Core Pillars for Your Athletic Lifestyle",
    scopeSubheading: "Comprehensive coverage ensuring consistency and physical safety at every step.",
    pillar1Title: "Intelligent Workouts",
    pillar1Desc: "Deterministic workout plans tailored to your equipment and experience.",
    pillar2Title: "Nutrition & Water",
    pillar2Desc: "Daily macronutrient targets and hydration logging.",
    pillar3Title: "Daily Readiness Check",
    pillar3Desc: "Pre-workout readiness scoring measuring fatigue and soreness.",
    pillar4Title: "Recovery & Sleep",
    pillar4Desc: "Sleep quality indicators and rest day recommendations.",
    pillar5Title: "Progress Tracking",
    pillar5Desc: "Workout history, streak monitoring, and goal tracking.",

    // 4 Value Pillars Bottom
    valueItem1Title: "Secure & Trusted",
    valueItem1Desc: "Data encryption & privacy protection at every step",
    valueItem2Title: "Personalized AI",
    valueItem2Desc: "Adaptive coaching aligned with your readiness and needs",
    valueItem3Title: "Comprehensive Tracking",
    valueItem3Desc: "Unified tracking for workouts, nutrition, and recovery",
    valueItem4Title: "Continuous Support",
    valueItem4Desc: "Smart plan updates based on your daily performance",

    // Product Areas Legacy Fallbacks
    productAreasHeading: "Everything You Need for Smarter, Safer Training",
    productAreasSubheading:
      "From personalized workouts to smart assessment and safe AI guidance, Rahafit unifies essential tools in one seamless experience.",

    // Safety & Personalization
    safetyHeading: "Safety & Intelligent Personalization",
    safetySubheading: "Your health and physical safety always come first.",
    safetyPoint1Title: "Adaptive to your information",
    safetyPoint1Desc:
      "Plans adapt to your logged fitness level, available equipment, and individual goals.",
    safetyPoint2Title: "Injury & safety boundary enforcement",
    safetyPoint2Desc:
      "If pain or high fatigue is reported, the system enforces safe substitutions or rest recommendations.",
    safetyPoint3Title: "Non-medical disclaimer",
    safetyPoint3Desc:
      "AI recommendations provide fitness and lifestyle guidance and do not replace professional medical diagnosis or advice.",

    // Pricing Placeholder / Info
    pricingHeading: "Simple & Transparent Access",
    pricingSubheading: "Start for free today and unlock full intelligent coaching capabilities.",
    pricingFreeTitle: "Free Discovery Tier",
    pricingFreeDesc: "Full access to smart assessment, workout tracking, and daily readiness check-in.",

    // Final CTA
    finalCtaHeading: "Ready to Start Your Journey?",
    finalCtaSubheading:
      "Create your account today and experience intelligent, safe, and personalized coaching.",
    finalCtaPrimary: "Create your account",
    finalCtaSecondary: "Sign in",

    // Floating Cards Copy
    heroCardStreak: "12 day streak",
    heroCardGoal: "Next goal: Lose 2 kg",
    heroCardCoach: "AI Coach: Live guidance",
    heroCardWorkout: "Workout ready — start when ready",

    // HUD Copy
    heroHudLabel: "SYSTEM INTERACTION HUD",
    heroHudStatus: "Optimizing recovery, movement, and daily readiness",

    landingValueTitle: "Why Choose Rahafit?",
    landingValue1Title: "Personalized Programming",
    landingValue1Desc: "Tailored workouts designed for your exact equipment and experience level.",
    landingValue2Title: "Safety Boundary Guard",
    landingValue2Desc:
      "Built-in medical declaration checks and active pain reporting during workouts.",
    landingValue3Title: "Comprehensive Tracking",
    landingValue3Desc:
      "Unified dashboard keeping workout history, nutrition logs, and progress in sync.",

    // Footer Copy
    footerDescription:
      "Intelligent training, adaptive nutrition, and safety-guided coaching for sustainable health.",
    footerContactHeading: "Contact & Support",
    footerContactNotice: "Contact information coming soon.",
  },
  ar: {
    // Header & Nav
    navBrand: "Rahafit",
    navFeatures: "المميزات",
    navHowItWorks: "كيف يعمل",
    navSafety: "الأمان والخصوصية",
    navPricing: "خطط الأسعار",
    navLogin: "تسجيل الدخول",
    navDiscover: "استكشف منصة Rahafit",
    navRegister: "أنشئ حسابك",

    // Hero Section Reference
    heroTrustBadge: "تدريب رياضي آمن، ذكي، وبناءً على خصوصيتك",
    landingHeroHeadline: "ابدأ رحلتك مع Rahafit",
    landingHeroSubheading:
      "تربط منصة Rahafit بين التخطيط الرياضي، متابعة التغذية، مؤشرات الاستشفاء، والتوجيه الذكي الذي يراعي أهدافك وحالتك في تجربة متكاملة واحدة.",
    landingHeroPrimaryCta: "أنشئ حسابك",
    landingHeroSecondaryCta: "استكشف المميزات",
    landingHeroTertiaryCta: "تخطي إلى تسجيل الدخول",
    heroHeading: "ابدأ رحلتك مع Rahafit",
    heroSubheading:
      "تربط منصة Rahafit بين التخطيط الرياضي، متابعة التغذية، مؤشرات الاستشفاء، والتوجيه الذكي الذي يراعي أمانك وصحتك في تجربة متكاملة واحدة.",
    heroPrimaryCta: "أنشئ حسابك",
    heroSecondaryCta: "استكشف المميزات",

    // How Rahafit Works Section
    howItWorksEyebrow: "كيف يعمل",
    howItWorksHeading: "رحلتك مع Rahafit في أربع خطوات",
    howItWorksSubheading:
      "من إنشاء الحساب إلى المتابعة اليومية، كل خطوة مصممة لتكون واضحة وآمنة ومخصصة لك.",
    step1Title: "أنشئ حسابك",
    step1Desc: "ابدأ خلال دقائق وسجّل بياناتك الأساسية بأمان.",
    step2Title: "حدّد أهدافك وحالتك",
    step2Desc: "أكمل التقييم الذكي لتوضيح أهدافك ومستوى جاهزيتك.",
    step3Title: "احصل على تجربة مخصصة",
    step3Desc: "يعتمد Rahafit على بياناتك لتقديم توجيه مناسب وآمن.",
    step4Title: "تابع تقدمك يوميًا",
    step4Desc: "راجع التمارين، التغذية، الجاهزية، والتقدم من لوحة واحدة.",
    howItWorksPrimaryCta: "ابدأ رحلتك",
    howItWorksSecondaryCta: "اكتشف المميزات",

    // Core Areas & Features Section
    featuresEyebrow: "المميزات الأساسية",
    featuresHeading: "كل ما تحتاجه لتدريب أذكى وأكثر أمانًا",
    featuresSubheading:
      "من التمرين المخصص إلى التقييم الذكي والتوجيه الآمن، تجمع Rahafit أهم الأدوات في تجربة واحدة.",
    featureWorkoutBadge: "ميزة أساسية",
    featureWorkoutTitle: "التمرين الذكي والتوجيه التدريبي",
    featureWorkoutDesc:
      "خطط تدريب حتمية متكيفة مع مستوى لياقتك وأدواتك المتاحة، مع إمكانية استبدال التمارين وتنبيهات الأمان المباشرة.",
    featureWorkoutPoint1: "خطة تدريب قابلة للتخصيص",
    featureWorkoutPoint2: "متابعة الألم والراحة",
    featureWorkoutPoint3: "بدائل آمنة للتمارين",
    featureWorkoutCta: "استكشف التمرين",

    featureAssessmentBadge: "تقييم آمن",
    featureAssessmentTitle: "التقييم الذكي والإقرار الصحي",
    featureAssessmentDesc:
      "حصر القيود الصحية ومستوى الرياضة لبناء ملف صحي متكامل يراعي سلامتك.",

    featureAiCoachBadge: "توجيه ذكي وآمن",
    featureAiCoachTitle: "المدرب الذكي والتوجيه الآمن",
    featureAiCoachDesc:
      "استفسارات فورية محكومة بقواعد الأمان. الإرشادات رياضية وليست تشخيصاً طبياً.",
    featureAiChip1: "تمارين",
    featureAiChip2: "تغذية",
    featureAiChip3: "تعافٍ",
    featureAiChip4: "تقدم",
    featureAiDisclaimer: "توجيهات نموذج الذكاء الاصطناعي هي إرشادات لأسلوب الحياة ولا بديل عن الاستشارة الطبية.",

    // Dashboard Preview Section
    previewEyebrow: "معاينة الواجهة",
    previewHeading: "لوحة تحكم ذكية تضع أهم بياناتك بين يديك",
    previewSubheading:
      "متابعة حية للجاهزية، التمرين، التغذية، وتوصيات المدرب الذكي في مكان واحد.",
    previewBadgeReadiness: "الجاهزية 88%",
    previewBadgeWorkout: "التمرين جاهز",
    previewBadgeNutrition: "أهداف الماكروز",
    previewInsightText: "مؤشرات التعافي ممتازة اليوم — يمكنك تنفيذ تمرين الجزء العلوي المخطط بثقة.",

    // AI Coach Showcase Section
    coachEyebrow: "المدرب الذكي",
    coachHeading: "استشارات رياضية آمنة محكومة بقواعد السلامة",
    coachSubheading:
      "احصل على توجيهات رياضية مخصصة تراعي إقرارك الصحي وحالتك البدنية.",
    coachSamplePrompt: "كيف أتمرن اليوم إذا كنت أشعر بإجهاد بسيط؟",
    coachSampleReply:
      "بناءً على إقرارك الصحي اليومي وجاهزيتك (88%)، تم تعديل كثافة التمرين وتقليل الأوزان 15% لحماية عضلاتك وضمان التعافي الآمن.",

    // Honest Quality Metrics Section
    trustMetric1Title: "نظام حتمي خاضع لقواعد الأمان",
    trustMetric1Desc: "فرض استبدال التمارين والراحة عند الإبلاغ عن ألم.",
    trustMetric2Title: "دعم كامل للعربية والإنجليزية",
    trustMetric2Desc: "تجربة عربية كاملة مع دعم اتجاه RTL و LTR.",
    trustMetric3Title: "خصوصية بيانات مشفرة لكل مستخدم",
    trustMetric3Desc: "مصادقة صارمة وعدم مشاركة البيانات بين الحسابات.",
    trustMetric4Title: "مفحوص ومثبت عبر 530+ اختبار",
    trustMetric4Desc: "محرك مثبت عبر اختبارات الوحدة والتكامل.",

    // Platform Scope Pillars
    scopeEyebrow: "نطاق المنصة",
    scopeHeading: "خمس ركائز أساسية لبناء لياقتك وأسلوب حياتك",
    scopeSubheading: "تغطية شاملة تضمن استمراريتك وسلامتك البدنية في كل خطوة.",
    pillar1Title: "التمرين الذكي",
    pillar1Desc: "خطط تدريب حتمية متكيفة مع معداتك ومستواك البدني.",
    pillar2Title: "التغذية والماء",
    pillar2Desc: "متابعة السعرات والماكروز واستهلاك الماء اليومي.",
    pillar3Title: "الفحص والجاهزية",
    pillar3Desc: "فحص الاستعداد البدني قبل بدء التمرين.",
    pillar4Title: "الاستشفاء والراحة",
    pillar4Desc: "مؤشرات جودة النوم وساعات التعافي.",
    pillar5Title: "متابعة التقدم",
    pillar5Desc: "سجل الجلسات، الأهداف، والاستمرارية.",

    // 4 Value Pillars Bottom
    valueItem1Title: "أمان وخصوصية",
    valueItem1Desc: "تشفير البيانات وحماية خصوصيتك في كل خطوة",
    valueItem2Title: "ذكاء اصطناعي محلي",
    valueItem2Desc: "توجيهات متكيفة تفهم مستوى جاهزيتك واحتياجاتك",
    valueItem3Title: "متابعة شاملة",
    valueItem3Desc: "تكامل التمارين، التغذية، وساعات التعافي",
    valueItem4Title: "دعم مستمر",
    valueItem4Desc: "تحديثات ذكية لخطتك بناءً على أدائك اليومي",

    // Product Areas Legacy Fallbacks
    productAreasHeading: "كل ما تحتاجه لتدريب أذكى وأكثر أمانًا",
    productAreasSubheading:
      "من التمرين المخصص إلى التقييم الذكي والتوجيه الآمن، تجمع Rahafit أهم الأدوات في تجربة واحدة.",

    // Safety & Personalization
    safetyHeading: "الأمان والتخصيص الذكي",
    safetySubheading: "صحتك وسلامتك البدنية تأتي دائماً في المقدمة.",
    safetyPoint1Title: "تتكيف الخطط مع بياناتك",
    safetyPoint1Desc:
      "تتأقلم التدريبات والبرامج بناءً على مستواك الرياضي، معداتك المتاحة، وأهدافك.",
    safetyPoint2Title: "احترام حدود الإصابات والسلامة",
    safetyPoint2Desc:
      "عند الإبلاغ عن ألم أو إجهاد مرتفع، يفرض النظام استبدال التمرين أو أخذ راحة آمنة.",
    safetyPoint3Title: "تنبيه طبي غير تشخيصي",
    safetyPoint3Desc:
      "التوجيه الذكي يقدم إرشادات رياضية ولأسلوب الحياة، ولا يحل محل الاستشارة أو التشخيص الطبي المتخصص.",

    // Pricing Placeholder / Info
    pricingHeading: "وصول بسيط وشفاف",
    pricingSubheading: "ابدأ مجاناً اليوم واستمتع بكل إمكانيات التدريب الذكي.",
    pricingFreeTitle: "الباقة المجانية الاستكشافية",
    pricingFreeDesc: "وصول كامل للتقييم الذكي، متابعة التمارين، وفحص الجاهزية اليومية.",

    // Final CTA
    finalCtaHeading: "جاهز تبدأ رحلتك؟",
    finalCtaSubheading: "أنشئ حسابك وابدأ تجربة Rahafit المخصصة اليوم.",
    finalCtaPrimary: "أنشئ حسابك",
    finalCtaSecondary: "تسجيل الدخول",

    // Floating Cards Copy
    heroCardStreak: "12 يوم متتالي",
    heroCardGoal: "هدفك القادم: خسارة 2 كجم",
    heroCardCoach: "المدرب الذكي: متابعة حية",
    heroCardWorkout: "التمرين جاهز — ابدأ لما تكون جاهز",

    // HUD Copy
    heroHudLabel: "SYSTEM INTERACTION HUD",
    heroHudStatus: "Optimizing recovery, movement, and daily readiness",

    landingValueTitle: "لماذا تختار Rahafit؟",
    landingValue1Title: "برامج تدريبية مخصصة",
    landingValue1Desc: "تمارين مصممة بدقة لتناسب أدواتك المتاحة ومستواك البدني الحالي.",
    landingValue2Title: "حماية وحدود آمنة",
    landingValue2Desc: "إقرار صحي دقيق وتقارير ألم فورية لضمان التمرين بدون مخاطر.",
    landingValue3Title: "متابعة شاملة ودقيقة",
    landingValue3Desc: "لوحة تحكم واحدة تربط سجل التمارين، الوجبات، ومستويات التقدم.",

    // Footer Copy
    footerDescription:
      "تمارين مخصصة، تغذية متوازنة، وتوجيه آمن يراعي صحتك وسلامتك البدنية في كل خطوة.",
    footerContactHeading: "التواصل والدعم",
    footerContactNotice: "معلومات التواصل قريباً.",
  },
};
