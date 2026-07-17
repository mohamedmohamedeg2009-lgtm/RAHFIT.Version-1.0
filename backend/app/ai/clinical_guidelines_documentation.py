"""
Clinical and Athletic Training Safety Reference Manual for RAHFIT AI.
This module contains detailed guidelines, protocols, and standard operating procedures
for coaches, athletic trainers, and clinical personnel using the RAHFIT AI platform.
"""

SAFETY_MANUAL_EN = """
================================================================================
                    RAHFIT AI - CLINICAL SAFETY MANUAL
================================================================================

1. CLINICAL GOALS & INTENT
The RAHFIT AI Decision Engine is designed to establish a safety-first, explainable
personalization layer for physical training, nutritional planning, and athletic
recovery. The target is to safeguard users by implementing deterministic clinical
checkpoints (gates) before adapting volume, intensity, or caloric intake.

2. CARDIOVASCULAR GATING PROTOCOLS
2.1 Risk Stratification
All users must complete a standardized intake screening (including PAR-Q+ and medical
history) to classify them into low, moderate, or high cardiovascular risk groups.
- LOW RISK: Asymptomatic individuals with fewer than two risk factors. Cleared for
  all exercise intensities.
- MODERATE RISK: Asymptomatic individuals with two or more risk factors. Cleared for
  moderate exercise; medical clearance strongly recommended before high intensity.
- HIGH RISK: Individuals with known cardiovascular, pulmonary, or metabolic disease.
  Exercise plan is blocked until professional medical clearance is verified.

2.2 Blood Pressure Thresholds
Exercise session must not be initiated if resting blood pressure exceeds 160 mmHg
systolic or 100 mmHg diastolic. If pressure exceeds 180/110 mmHg, it constitutes
an emergency blocker.

3. METABOLIC DISEASE PROTOCOLS
3.1 Glycemic Controls (Diabetes Mellitus)
Users with Type 1 or Type 2 Diabetes must measure capillary blood glucose prior to
every training session.
- Glucose < 100 mg/dL: Consume 15-30g of fast-acting carbohydrates and re-test.
- Glucose 100-250 mg/dL: Safe range to initiate training.
- Glucose > 250 mg/dL with ketones: Training session is completely blocked.
- Glucose > 300 mg/dL without ketones: Exercise with caution, restrict RPE to 6.

3.2 Respiratory Controls (Severe Asthma)
Severe asthmatics must:
- Ensure rescue bronchodilator is physically present at the training station.
- Perform a specialized 15-minute warm-up to utilize the physiological refractory period.
- Immediately terminate the session if wheezing or persistent dry cough occurs.

4. MUSCULOSKELETAL REHABILITATION AND SUBSTITUTIONS
4.1 Active Injury Management
If the user reports an active localized injury (e.g., knee pain, shoulder impingement,
lumbar disc strain), the decision engine flags affected muscle groups and automatically
substitutes high-shear movements with low-impact alternatives:
- Knee Pain: Replace barbell back squat with Spanish Squat or isometric wall sit.
- Shoulder Pain: Replace bench press with floor press; replace overhead press with landmine press.
- Lumbar Strain: Replace conventional deadlifts with high-handle trap bar deadlifts or planks.
"""

SAFETY_MANUAL_AR = """
================================================================================
                 دليل السلامة السريرية والتدريب الرياضي - RAHFIT AI
================================================================================

1. الأهداف والغايات السريرية
تم تصميم محرك اتخاذ القرار RAHFIT AI لإنشاء طبقة تخصيص آمنة وقابلة للتفسير للتدريب البدني
والتخطيط الغذائي والاستشفاء الرياضي. الهدف هو حماية المستخدمين من خلال تطبيق نقاط تفتيش
سريرية حتمية (بوابات السلامة) قبل تعديل حجم التمرين أو شدته أو السعرات الحرارية.

2. بروتوكولات حماية القلب والأوعية الدموية
2.1 تصنيف المخاطر
يجب على جميع المستخدمين إكمال فحص أولي موحد (بما في ذلك PAR-Q + والتاريخ الطبي) لتصنيفهم
إلى مجموعات مخاطر القلب والأوعية الدموية المنخفضة أو المتوسطة أو العالية.
- مخاطر منخفضة: الأفراد الذين لا يعانون من أعراض ولديهم أقل من عاملين من عوامل الخطر.
  مصرح لهم بجميع مستويات التمرين.
- مخاطر متوسطة: الأفراد الذين لا يعانون من أعراض ولديهم عاملان أو أكثر من عوامل الخطر.
  مصرح لهم بالتمارين المعتدلة؛ ويوصى بشدة بالحصول على تصريح طبي قبل التمارين عالية الشدة.
- مخاطر عالية: الأفراد الذين يعانون من أمراض معروفة في القلب أو الأوعية الدموية أو الرئتين
  أو التمثيل الغذائي. يتم حظر خطة التمرين حتى يتم التحقق من التصريح الطبي المعتمد.

2.2 حدود ضغط الدم
يجب عدم بدء جلسة التمرين إذا تجاوز ضغط الدم أثناء الراحة 160 ملم زئبق انقباضي أو 100 ملم
زئبق انبساطي. إذا تجاوز الضغط 180/110 ملم زئبق، فإن ذلك يمثل مانعاً طارئاً.

3. بروتوكولات أمراض التمثيل الغذائي
3.1 التحكم في نسبة السكر في الدم (داء السكري)
يجب على المستخدمين المصابين بداء السكري من النوع الأول أو الثاني قياس مستوى السكر في الدم
قبل كل جلسة تدريبية.
- السكر < 100 ملغ/ديسيلتر: تناول 15-30 جراماً من الكربوهيدرات سريعة المفعول وأعد الاختبار.
- السكر 100-250 ملغ/ديسيلتر: النطاق الآمن لبدء التدريب.
- السكر > 250 ملغ/ديسيلتر مع وجود الكيتونات: يتم حظر جلسة التدريب تماماً.
- السكر > 300 ملغ/ديسيلتر بدون كيتونات: تمرن بحذر، وحدد معدل الجهد المحسوس عند 6.

3.2 التحكم في الجهاز التنفسي (الربو الشديد)
يجب على مرضى الربو الشديد:
- التأكد من وجود موسع الشعب الهوائية الإسعافي بشكل مادي في محطة التدريب.
- أداء إحماء متخصص لمدة 15 دقيقة للاستفادة من فترة الممانعة الفسيولوجية.
- إنهاء الجلسة فوراً في حالة حدوث أزيز أو سعال جاف مستمر.

4. إعادة تأهيل الجهاز العضلي الهيكلي والاستبدال
4.1 إدارة الإصابات النشطة
إذا أبلغ المستخدم عن إصابة موضعية نشطة (مثل ألم الركبة، اصطدام الكتف، إجهاد القرص القطني)،
يقوم محرك اتخاذ القرار بوضع علامة على المجموعات العضلية المتأثرة ويستبدل تلقائياً الحركات ذات قوى
القص العالية ببدائل منخفضة التأثير:
- ألم الركبة: استبدل القرفصاء بالبار بالقرفصاء الإسبانية أو الجلوس الثابت على الحائط.
- ألم الكتف: استبدل ضغط البنش بضغط الأرض؛ واستبدل الدفع فوق الرأس بدفع المايندلاين.
- إجهاد أسفل الظهر: استبدل الرفعة المميتة التقليدية برفع قضيب التراب بمقابض مرتفعة أو تمارين اللوح.
"""
