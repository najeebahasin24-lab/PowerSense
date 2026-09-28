import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(output_path="AI_Based_Smart_Transformer_Health_Monitoring_Presentation.pptx"):
    prs = Presentation()
    # 4:3 slide dimensions (720x540 pt = 10.0 x 7.5 inches)
    prs.slide_width = Inches(10.0)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    RED_TITLE = RGBColor(192, 0, 0)       # Template crimson red for main title (c00000)
    NAVY_LINE = RGBColor(31, 78, 121)     # Template navy blue accent line (1F4E79)
    TEXT_BLACK = RGBColor(0, 0, 0)        # Pure black for all text - no color used in text
    FOOTER_GRAY = RGBColor(137, 137, 137) # Template footer gray (898989)

    EMBLEM_IMG = "extracted_assets/p1_img1_23.jpeg"
    TOP_LOGO_IMG = "extracted_assets/p1_img2_24.jpeg"
    ARCH_IMG = "extracted_assets/system_architecture_diagram.png"
    QA_IMG = "extracted_assets/p15_img2_829.jpeg"
    THANKYOU_IMG = "extracted_assets/p16_img2_839.jpeg"

    FONT_MAIN = "Calibri"

    def add_common_header_footer(slide, title_text, slide_number):
        # Top university emblem (small circular badge top-right)
        if os.path.exists(EMBLEM_IMG):
            slide.shapes.add_picture(EMBLEM_IMG, Inches(8.85), Inches(0.22), width=Inches(0.85))

        # Title Text Box
        title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(8.1), Inches(0.85))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = FONT_MAIN
        p.font.size = Pt(34)
        p.font.bold = True
        p.font.color.rgb = RED_TITLE
        p.alignment = PP_ALIGN.CENTER

        # Horizontal Navy Blue Divider Line
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(1.22), Inches(9.2), Inches(0.025)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = NAVY_LINE
        line.line.color.rgb = NAVY_LINE

        # Footer Date (Left)
        d_box = slide.shapes.add_textbox(Inches(0.4), Inches(6.98), Inches(2.5), Inches(0.35))
        d_tf = d_box.text_frame
        d_tf.word_wrap = True
        dp = d_tf.paragraphs[0]
        dp.text = "22 September 2026"
        dp.font.name = FONT_MAIN
        dp.font.size = Pt(12)
        dp.font.color.rgb = FOOTER_GRAY

        # Footer Department (Center)
        c_box = slide.shapes.add_textbox(Inches(2.8), Inches(6.88), Inches(4.8), Inches(0.5))
        c_tf = c_box.text_frame
        c_tf.word_wrap = True
        cp = c_tf.paragraphs[0]
        cp.text = "Department of Computer Science\nand Engineering"
        cp.font.name = FONT_MAIN
        cp.font.size = Pt(13)
        cp.font.color.rgb = TEXT_BLACK
        cp.alignment = PP_ALIGN.CENTER

        # Footer Slide Number (Right)
        num_box = slide.shapes.add_textbox(Inches(8.8), Inches(6.98), Inches(0.8), Inches(0.35))
        num_tf = num_box.text_frame
        num_p = num_tf.paragraphs[0]
        num_p.text = str(slide_number)
        num_p.font.name = FONT_MAIN
        num_p.font.size = Pt(12)
        num_p.font.color.rgb = FOOTER_GRAY
        num_p.alignment = PP_ALIGN.RIGHT

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_slide_layout)
    if os.path.exists(TOP_LOGO_IMG):
        s1.shapes.add_picture(TOP_LOGO_IMG, Inches(1.85), Inches(0.32), width=Inches(6.3))

    # Subject Code Text (Red as in template)
    sc_box = s1.shapes.add_textbox(Inches(0.5), Inches(2.35), Inches(9.0), Inches(1.15))
    sc_tf = sc_box.text_frame
    sc_tf.word_wrap = True
    p1 = sc_tf.paragraphs[0]
    p1.text = "Subject Code"
    p1.font.name = FONT_MAIN
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = RED_TITLE
    p1.alignment = PP_ALIGN.CENTER

    p2 = sc_tf.add_paragraph()
    p2.text = "PT I - INTERDISCIPLINARY PROJECT"
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = RED_TITLE
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(4)

    # Project Title (Pure black text, 24 pt)
    pt_box = s1.shapes.add_textbox(Inches(0.5), Inches(3.75), Inches(9.0), Inches(1.2))
    pt_tf = pt_box.text_frame
    pt_tf.word_wrap = True
    tp1 = pt_tf.paragraphs[0]
    tp1.text = "AI-BASED SMART TRANSFORMER HEALTH MONITORING SYSTEM"
    tp1.font.name = FONT_MAIN
    tp1.font.size = Pt(23)
    tp1.font.bold = True
    tp1.font.color.rgb = TEXT_BLACK
    tp1.alignment = PP_ALIGN.CENTER

    tp2 = pt_tf.add_paragraph()
    tp2.text = "Review 1 - Project Idea & Proposed System"
    tp2.font.name = FONT_MAIN
    tp2.font.size = Pt(16)
    tp2.font.color.rgb = TEXT_BLACK
    tp2.alignment = PP_ALIGN.CENTER
    tp2.space_before = Pt(4)

    # Student Details (Bottom Left)
    st_box = s1.shapes.add_textbox(Inches(0.6), Inches(5.15), Inches(5.2), Inches(1.4))
    st_tf = st_box.text_frame
    st_tf.word_wrap = True
    stp1 = st_tf.paragraphs[0]
    stp1.text = "1. S Najeeba Hasin [ Reg.No. : 44731153 ]"
    stp1.font.name = FONT_MAIN
    stp1.font.size = Pt(16)
    stp1.font.bold = True
    stp1.font.color.rgb = TEXT_BLACK

    stp2 = st_tf.add_paragraph()
    stp2.text = "2. Saumya Kumari [ Reg.No. : 44731080 ]"
    stp2.font.name = FONT_MAIN
    stp2.font.size = Pt(16)
    stp2.font.bold = True
    stp2.font.color.rgb = TEXT_BLACK
    stp2.space_before = Pt(8)

    # Internal Guide Details (Bottom Right)
    g_box = s1.shapes.add_textbox(Inches(6.0), Inches(5.15), Inches(3.6), Inches(1.4))
    g_tf = g_box.text_frame
    g_tf.word_wrap = True
    gp1 = g_tf.paragraphs[0]
    gp1.text = "Internal Guide"
    gp1.font.name = FONT_MAIN
    gp1.font.size = Pt(16)
    gp1.font.bold = True
    gp1.font.color.rgb = TEXT_BLACK

    gp2 = g_tf.add_paragraph()
    gp2.text = "Shanmuga Priya M.E."
    gp2.font.name = FONT_MAIN
    gp2.font.size = Pt(16)
    gp2.font.bold = True
    gp2.font.color.rgb = TEXT_BLACK
    gp2.space_before = Pt(8)

    # Footer for Slide 1
    d1 = s1.shapes.add_textbox(Inches(0.4), Inches(6.98), Inches(2.5), Inches(0.35))
    d1.text_frame.paragraphs[0].text = "22 September 2026"
    d1.text_frame.paragraphs[0].font.name = FONT_MAIN
    d1.text_frame.paragraphs[0].font.size = Pt(12)
    d1.text_frame.paragraphs[0].font.color.rgb = FOOTER_GRAY

    c1 = s1.shapes.add_textbox(Inches(2.8), Inches(6.88), Inches(4.8), Inches(0.5))
    c1p = c1.text_frame.paragraphs[0]
    c1p.text = "Department of Computer Science\nand Engineering"
    c1p.font.name = FONT_MAIN
    c1p.font.size = Pt(13)
    c1p.font.color.rgb = TEXT_BLACK
    c1p.alignment = PP_ALIGN.CENTER

    n1 = s1.shapes.add_textbox(Inches(8.8), Inches(6.98), Inches(0.8), Inches(0.35))
    n1.text_frame.paragraphs[0].text = "1"
    n1.text_frame.paragraphs[0].font.name = FONT_MAIN
    n1.text_frame.paragraphs[0].font.size = Pt(12)
    n1.text_frame.paragraphs[0].font.color.rgb = FOOTER_GRAY
    n1.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT

    # ==========================================
    # SLIDE 2: Presentation Outline
    # ==========================================
    s2 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s2, "PRESENTATION OUTLINE", 2)
    s2_box = s2.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(8.4), Inches(5.3))
    s2_tf = s2_box.text_frame
    s2_tf.word_wrap = True

    outline_items = [
        "COURSE CERTIFICATE",
        "ABSTRACT",
        "OBJECTIVES",
        "SYSTEM ARCHITECTURE",
        "HARDWARE AND SOFTWARE REQUIREMENTS",
        "MINI TRANSFORMER & SENSOR SETUP",
        "AI / ML HEALTH EVALUATION LOGIC",
        "RESULTS AND DISCUSSIONS",
        "RESULT SNAPSHOTS",
        "CONCLUSION & FUTURE WORK",
        "REFERENCES"
    ]
    for idx, item in enumerate(outline_items):
        p = s2_tf.paragraphs[0] if idx == 0 else s2_tf.add_paragraph()
        p.text = f"•   {item}"
        p.font.name = FONT_MAIN
        p.font.size = Pt(19)  # Max readable size filling the slide
        p.font.color.rgb = TEXT_BLACK
        p.space_after = Pt(7)

    # ==========================================
    # SLIDE 3: Course Certificate (Kept Blank)
    # ==========================================
    s3 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s3, "COURSE CERTIFICATE", 3)
    # Kept completely empty in the center area

    # ==========================================
    # SLIDE 4: Abstract
    # ==========================================
    s4 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s4, "ABSTRACT", 4)
    s4_box = s4.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(5.2))
    s4_tf = s4_box.text_frame
    s4_tf.word_wrap = True

    abs_points = [
        "Distribution transformers are vital electrical grid assets; unnoticed faults lead to unexpected power blackouts, costly downtime, and severe equipment damage.",
        "Conventional maintenance relies on intermittent manual inspections, which cannot detect sudden thermal spikes, overloads, or insulation failures in real time.",
        "This project presents an AIoT-based hardware monitoring system built using a mini transformer testbed.",
        "Four physical sensors are interfaced with an ESP32 microcontroller: Temperature, Oil Level, AC Voltage, and Load Current.",
        "Sensor data is uploaded to a cloud database where an AI/ML health assessment model classifies transformer condition into NORMAL, WARNING, or CRITICAL/DANGEROUS.",
        "Power grid officials can monitor live telemetry, dynamic trend graphs, and instant fault alerts through a real-time web portal."
    ]
    for idx, txt in enumerate(abs_points):
        p = s4_tf.paragraphs[0] if idx == 0 else s4_tf.add_paragraph()
        p.text = f"•   {txt}"
        p.font.name = FONT_MAIN
        p.font.size = Pt(18)  # Optimal font size making slide full and clear
        p.font.color.rgb = TEXT_BLACK
        p.space_after = Pt(10)

    # ==========================================
    # SLIDE 5: Objectives
    # ==========================================
    s5 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s5, "OBJECTIVES", 5)
    s5_box = s5.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(5.2))
    s5_tf = s5_box.text_frame
    s5_tf.word_wrap = True

    objs = [
        "1.  To develop an AIoT hardware monitoring unit using a mini transformer testbed with physical sensors.",
        "2.  To interface Temperature, Oil Level, AC Voltage, and Current sensors with an ESP32 microcontroller for continuous real-time data acquisition.",
        "3.  To transmit live sensor measurements wirelessly from the ESP32 to a cloud database and backend server.",
        "4.  To implement an AI/ML analysis engine to evaluate parameter thresholds and determine if the transformer is in Normal, Warning, or Critical condition.",
        "5.  To build a real-time web monitoring dashboard for power grid officials displaying live readings, parameter trend graphs, and alert notifications."
    ]
    for idx, desc in enumerate(objs):
        p = s5_tf.paragraphs[0] if idx == 0 else s5_tf.add_paragraph()
        p.text = desc
        p.font.name = FONT_MAIN
        p.font.size = Pt(18)
        p.font.color.rgb = TEXT_BLACK
        p.space_after = Pt(14)

    # ==========================================
    # SLIDE 6: System Architecture (With Picture/Diagram)
    # ==========================================
    s6 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s6, "SYSTEM ARCHITECTURE", 6)
    if os.path.exists(ARCH_IMG):
        s6.shapes.add_picture(ARCH_IMG, Inches(0.5), Inches(1.35), width=Inches(9.0), height=Inches(5.4))

    # ==========================================
    # SLIDE 7: Hardware and Software Requirements
    # ==========================================
    s7 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s7, "HARDWARE AND SOFTWARE REQUIREMENTS", 7)
    s7_box = s7.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(8.4), Inches(5.3))
    s7_tf = s7_box.text_frame
    s7_tf.word_wrap = True

    p = s7_tf.paragraphs[0]
    p.text = "•   Hardware Requirements"
    p.font.name = FONT_MAIN
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = TEXT_BLACK
    p.space_after = Pt(4)

    hw_items = [
        "Mini Step-Down Transformer  –  Laboratory prototype testbed",
        "ESP32 Microcontroller  –  32-bit Dual Core with built-in Wi-Fi & ADC",
        "Temperature Sensor (LM35 / DS18B20)  –  Core and oil thermal monitoring",
        "Current Sensor (ACS712)  –  Secondary load current measurement",
        "Voltage Sensor (ZMPT101B)  –  AC potential transformer module",
        "Oil Level Sensor (Ultrasonic / Float)  –  Dielectric oil level measurement"
    ]
    for h in hw_items:
        hp = s7_tf.add_paragraph()
        hp.text = f"–   {h}"
        hp.font.name = FONT_MAIN
        hp.font.size = Pt(17)
        hp.font.color.rgb = TEXT_BLACK
        hp.space_after = Pt(3)

    sp = s7_tf.add_paragraph()
    sp.text = "•   Software Requirements"
    sp.font.name = FONT_MAIN
    sp.font.size = Pt(21)
    sp.font.bold = True
    sp.font.color.rgb = TEXT_BLACK
    sp.space_before = Pt(8)
    sp.space_after = Pt(4)

    sw_items = [
        "Arduino IDE  –  Embedded C++ programming for ESP32 sensor acquisition",
        "Python (FastAPI)  –  Backend REST and WebSocket communication server",
        "Cloud Database / SQLite  –  Storage for time-series telemetry records",
        "Web Technologies (HTML, CSS, JavaScript, Chart.js)  –  Official dashboard"
    ]
    for s in sw_items:
        swp = s7_tf.add_paragraph()
        swp.text = f"–   {s}"
        swp.font.name = FONT_MAIN
        swp.font.size = Pt(17)
        swp.font.color.rgb = TEXT_BLACK
        swp.space_after = Pt(3)

    # ==========================================
    # SLIDE 8: Mini Transformer & Sensor Setup
    # ==========================================
    s8 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s8, "MINI TRANSFORMER & SENSOR SETUP", 8)
    s8_box = s8.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(8.4), Inches(5.3))
    s8_tf = s8_box.text_frame
    s8_tf.word_wrap = True

    p = s8_tf.paragraphs[0]
    p.text = "•   Monitored Parameters on the Mini Transformer Testbed:"
    p.font.name = FONT_MAIN
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_BLACK
    p.space_after = Pt(8)

    sensors = [
        ("Temperature Sensor (°C):",
         "Continuously tracks thermal buildup in transformer windings and insulating oil. Prevents thermal degradation and core insulation failure."),
        ("Load Current Sensor (A):",
         "Measures the real-time load current drawn across secondary output terminals. Immediately identifies overcurrent surges and short-circuit faults."),
        ("AC Voltage Sensor (V):",
         "Monitors terminal AC voltage fluctuations. Identifies abnormal grid voltage sags, brownouts, and overvoltage conditions."),
        ("Oil Level Sensor (%):",
         "Measures dielectric and cooling oil level in the reservoir. Warns officials when oil depletes below safe operating levels to avoid overheating.")
    ]
    for name, desc in sensors:
        sp = s8_tf.add_paragraph()
        sp.text = f"–   {name}  {desc}"
        sp.font.name = FONT_MAIN
        sp.font.size = Pt(17.5)
        sp.font.color.rgb = TEXT_BLACK
        sp.space_after = Pt(8)

    # ==========================================
    # SLIDE 9: AI / ML Health Evaluation Logic
    # ==========================================
    s9 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s9, "AI / ML HEALTH EVALUATION LOGIC", 9)
    s9_box = s9.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(8.4), Inches(5.3))
    s9_tf = s9_box.text_frame
    s9_tf.word_wrap = True

    logic_points = [
        ("•   Multi-Parameter Condition Evaluation",
         "The cloud-hosted AI/ML engine continuously processes incoming multi-sensor telemetry (Temperature, Current, Voltage, Oil Level) to determine the transformer's real-time operational state."),
        ("•   Three-Tier Health Classification", ""),
        ("     –   NORMAL:", " All 4 parameters operate within standard safety margins under normal load."),
        ("     –   WARNING:", " Early anomaly detected (e.g. rising temperature or elevated current); alerts officials for preventive inspection."),
        ("     –   CRITICAL / DANGEROUS:", " Hazardous conditions detected (e.g. high temperature with low oil level or heavy overload); requires prompt load-shedding and shutdown."),
        ("•   Future Machine Learning Integration",
         "Continuous data logging builds a historical operational dataset to train predictive machine learning models for Remaining Useful Life (RUL) estimation.")
    ]
    for idx, (title, body) in enumerate(logic_points):
        p = s9_tf.paragraphs[0] if idx == 0 else s9_tf.add_paragraph()
        p.text = f"{title}{body}"
        p.font.name = FONT_MAIN
        p.font.size = Pt(17.5)
        p.font.color.rgb = TEXT_BLACK
        if "NORMAL:" in title or "WARNING:" in title or "CRITICAL" in title:
            p.space_after = Pt(4)
        else:
            p.space_after = Pt(9)

    # ==========================================
    # SLIDE 10: Results and Discussion (EMPTY for Review 1)
    # ==========================================
    s10 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s10, "RESULTS AND DISCUSSION", 10)
    # Kept completely empty in body per user request (Review 1: project not yet completed)

    # ==========================================
    # SLIDE 11: Result Snapshots (EMPTY for Review 1)
    # ==========================================
    s11 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s11, "RESULT SNAPSHOTS", 11)
    # Kept completely empty in body per user request (Review 1: project not yet completed)

    # ==========================================
    # SLIDE 12: Results and Discussion (EMPTY for Review 1)
    # ==========================================
    s12 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s12, "RESULTS AND DISCUSSION", 12)
    # Kept completely empty in body per user request (Review 1: project not yet completed)

    # ==========================================
    # SLIDE 13: Conclusion & Future Work
    # ==========================================
    s13 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s13, "CONCLUSION & FUTURE WORK", 13)
    s13_box = s13.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(8.4), Inches(5.3))
    s13_tf = s13_box.text_frame
    s13_tf.word_wrap = True

    p = s13_tf.paragraphs[0]
    p.text = "•   Conclusion"
    p.font.name = FONT_MAIN
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = TEXT_BLACK
    p.space_after = Pt(4)

    conc_items = [
        "Proposed an end-to-end AIoT hardware monitoring system using a mini transformer testbed.",
        "Replaces intermittent manual inspection with continuous, automated multi-sensor data acquisition.",
        "Designed an AI/ML health evaluation model to classify conditions into NORMAL, WARNING, or CRITICAL.",
        "Proposed a real-time web portal enabling power grid officials to observe live parameters and active alerts."
    ]
    for c in conc_items:
        cp = s13_tf.add_paragraph()
        cp.text = f"–   {c}"
        cp.font.name = FONT_MAIN
        cp.font.size = Pt(17)
        cp.font.color.rgb = TEXT_BLACK
        cp.space_after = Pt(3)

    fp = s13_tf.add_paragraph()
    fp.text = "•   Future Work"
    fp.font.name = FONT_MAIN
    fp.font.size = Pt(21)
    fp.font.bold = True
    fp.font.color.rgb = TEXT_BLACK
    fp.space_before = Pt(8)
    fp.space_after = Pt(4)

    fut_items = [
        "Train predictive machine learning algorithms (e.g. Random Forest, LSTM) for Remaining Useful Life (RUL) forecasting.",
        "Scale the prototype hardware with industrial-grade Current Transformers (CT) and Potential Transformers (PT).",
        "Integrate automated GSM/SMS emergency alerts to notify field maintenance personnel instantly."
    ]
    for f in fut_items:
        fpp = s13_tf.add_paragraph()
        fpp.text = f"–   {f}"
        fpp.font.name = FONT_MAIN
        fpp.font.size = Pt(17)
        fpp.font.color.rgb = TEXT_BLACK
        fpp.space_after = Pt(3)

    # ==========================================
    # SLIDE 14: References
    # ==========================================
    s14 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s14, "REFERENCES", 14)
    s14_box = s14.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(5.2))
    s14_tf = s14_box.text_frame
    s14_tf.word_wrap = True

    refs = [
        "1.  IEEE Std C57.104-2019: 'IEEE Guide for the Interpretation of Gases Generated in Mineral Oil-Immersed Transformers,' IEEE Standards Association.",
        "2.  A. S. Farag, et al., 'Online Condition Monitoring and Diagnostic Systems for Power Transformers,' IEEE Power Engineering Review, vol. 22, no. 10.",
        "3.  Espressif Systems, 'ESP32 Series Microcontroller Hardware Reference and Networking Specifications,' Technical Manual, 2024.",
        "4.  FastAPI Framework Documentation: 'High-performance Python Web APIs for Real-Time IoT Systems,' https://fastapi.tiangolo.com/.",
        "5.  Chart.js Documentation: 'Open-Source HTML5 Canvas Data Visualization Library for IoT Dashboards,' https://www.chartjs.org/."
    ]
    for idx, r in enumerate(refs):
        p = s14_tf.paragraphs[0] if idx == 0 else s14_tf.add_paragraph()
        p.text = r
        p.font.name = FONT_MAIN
        p.font.size = Pt(17.5)
        p.font.color.rgb = TEXT_BLACK
        p.space_after = Pt(12)

    # ==========================================
    # SLIDE 15: Questions & Answers (Q&A)
    # ==========================================
    s15 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s15, "AI-BASED SMART TRANSFORMER HEALTH MONITORING", 15)
    if os.path.exists(QA_IMG):
        s15.shapes.add_picture(QA_IMG, Inches(2.7), Inches(2.2), width=Inches(4.6))

    qa_box = s15.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(8.0), Inches(1.0))
    qa_tf = qa_box.text_frame
    qp = qa_tf.paragraphs[0]
    qp.text = "QUESTIONS & ANSWERS"
    qp.font.name = FONT_MAIN
    qp.font.size = Pt(24)
    qp.font.bold = True
    qp.font.color.rgb = TEXT_BLACK
    qp.alignment = PP_ALIGN.CENTER

    qp2 = qa_tf.add_paragraph()
    qp2.text = "Open for Questions, Evaluation & Feedback"
    qp2.font.name = FONT_MAIN
    qp2.font.size = Pt(16)
    qp2.font.color.rgb = TEXT_BLACK
    qp2.alignment = PP_ALIGN.CENTER
    qp2.space_before = Pt(4)

    # ==========================================
    # SLIDE 16: Thank You
    # ==========================================
    s16 = prs.slides.add_slide(blank_slide_layout)
    add_common_header_footer(s16, "AI-BASED SMART TRANSFORMER HEALTH MONITORING", 16)
    if os.path.exists(THANKYOU_IMG):
        s16.shapes.add_picture(THANKYOU_IMG, Inches(1.7), Inches(2.1), width=Inches(6.6))

    prs.save(output_path)
    print(f"Successfully generated presentation at: {output_path}")

if __name__ == '__main__':
    create_presentation()
