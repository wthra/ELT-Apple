🍎 Apple (AAPL) Market Sentiment Pipeline
Automated Data Engineering Project: วิเคราะห์ความสัมพันธ์ระหว่างข่าวสาร (Sentiment) และราคาหุ้นผ่านระบบ ELT Pipeline อัตโนมัติ

โปรเจกต์นี้สาธิตการสร้าง Modern Data Stack บนเครื่อง Local โดยจำลองระบบ Data Lakehouse ขนาดย่อม เพื่อรวบรวมข้อมูลราคาหุ้นจาก Yahoo Finance และข่าวสาร นำมาประมวลผลหาค่า Sentiment (NLP) และจัดเก็บลง Warehouse เพื่อแสดงผลผ่าน Dashboard


Orchestrator	🍃 Apache Airflow	ควบคุม Workflow และตั้งเวลาทำงาน (Daily Schedule)
Storage	🪣 MinIO	S3-Compatible Object Storage สำหรับทำ Data Lake
Compute	🦆 DuckDB	In-process OLAP database สำหรับประมวลผล SQL ความเร็วสูง
Transformation	🐼 Pandas / TextBlob	Python libraries สำหรับ Data Manipulation และ NLP
Quality	✅ Pandera	ตรวจสอบ Schema และคุณภาพข้อมูล (Data Validation)
Frontend	📊 Streamlit	Interactive Dashboard สำหรับดูผลลัพธ์ Real-time
Container	🐳 Docker	จัดการ Environment ทั้งหมดผ่าน Docker Compose




⚙️ How it Works (System Workflow)ระบบทำงานแบบ ELT (Extract - Load - Transform) โดยมีลำดับการทำงานดังนี้:Ingest: Airflow สั่งดึงข้อมูลราคาหุ้นล่าสุด (Real-time) และโหลดไฟล์ข่าวเข้าสู่ MinIO (Raw Bucket)Process: สคริปต์ Python ดึงข้อมูลดิบมาทำความสะอาด และใช้ TextBlob ให้คะแนนความรู้สึกของข่าว (Sentiment Score: -1 ถึง +1)Validate: ตรวจสอบความถูกต้องด้วย Pandera (เช่น ราคาต้องไม่ติดลบ)Warehouse: บันทึกข้อมูลที่ผ่านการตรวจสอบแล้วลง DuckDB เพื่อเตรียม QueryVisualize: API และ Dashboard ดึงข้อมูลจาก DuckDB ไปแสดงผล🚀 Quick Start Guideเริ่มต้นใช้งานระบบภายใน 3 ขั้นตอน:1. Clone & Setupเตรียม Environment และติดตั้ง Library ที่จำเป็นBashgit clone <your-repo-url>
cd <project-folder>
pip install -r requirements.txt
2. Launch Infrastructureรันคำสั่ง Docker Compose เพื่อสร้าง Container ของ Airflow, MinIO และ Postgres (ระบบจะสร้าง Image ใหม่ที่มี Library ครบถ้วน)Bashdocker-compose up -d --build
Note: รอสักครู่เพื่อให้ Airflow Webserver เริ่มทำงานสมบูรณ์3. Run Pipeline & Dashboardคุณสามารถควบคุมระบบได้ 2 ช่องทาง:Option A: ผ่าน Airflow UIเข้าเว็บ http://localhost:8080 (Log in: admin/admin)เปิดใช้งาน DAG: aapl_elt_pipelineOption B: ผ่าน Dashboard (แนะนำ)รันคำสั่ง:Bashstreamlit run dashboard.py
กดปุ่ม "🔄 Run Pipeline" บนหน้าเว็บเพื่อดึงข้อมูลล่าสุดทันที🔌 API Endpointsมี Flask API ให้บริการสำหรับดึงข้อมูลไปใช้ต่อ (python api.py):MethodEndpointDescriptionGET/api/v1/stock_summaryข้อมูลสรุปหุ้นย้อนหลัง 7 วันGET/api/v1/sentiment_vs_priceข้อมูล Correlation ทั้งหมดสำหรับนำไปพลอตกราฟ📂 Repository LayoutPlaintext.
├── dags/               # Airflow Scripts (DAGs & Pipeline Logic)
├── data/               # Local Data Mapping (Raw, Processed, DB)
├── docker-compose.yaml # Infrastructure Configuration
├── dashboard.py        # User Interface (Streamlit)
├── api.py              # Backend API (Flask)
└── requirements.txt    # Project Dependencies
