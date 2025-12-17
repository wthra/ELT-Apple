# 🍏 Apple Market Pulse: Sentiment-Driven ELT Engine

> **A containerized data platform** that correlates financial market trends with media sentiment using a modern local data stack.

โปรเจกต์นี้คือระบบ Data Engineering แบบครบวงจร (End-to-End) ที่ถูกออกแบบมาเพื่อดึงข้อมูลราคาหุ้น AAPL และข่าวสาร นำมาประมวลผลหาความสัมพันธ์ (Correlation) และตรวจสอบคุณภาพข้อมูลอัตโนมัติ พร้อมรองรับการแสดงผลผ่าน Interactive Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-Orchestration-017CEE?style=flat-square&logo=apache-airflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=flat-square&logo=docker&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-S3%20Storage-C72C48?style=flat-square&logo=minio&logoColor=white)

---

## ⚡ System Capabilities

จุดเด่นของระบบที่ถูกพัฒนาขึ้น:

* **⏱️ Automated Ingestion:** ท่อส่งข้อมูล (Pipeline) ทำงานอัตโนมัติทุกวันเวลา 01:00 น. ผ่าน Airflow
* **🧠 NLP Processing:** วิเคราะห์อารมณ์ของข่าว (Sentiment Analysis) ด้วย TextBlob Library
* **🛡️ Quality Gate:** มีระบบป้องกันข้อมูลผิดพลาด (Data Validation) ด้วย Pandera ก่อนบันทึกลงฐานข้อมูล
* **🦆 High-Speed SQL:** ใช้ DuckDB เป็น Data Warehouse เพื่อการเรียกดูข้อมูลที่รวดเร็ว (OLAP)
* **📉 Interactive UI:** หน้า Dashboard สามารถ Filter ช่วงเวลาและสั่งรัน Pipeline ได้ทันที

---

## 🛠️ Technology Stack

| Domain | Tool | Role in Project |
| :--- | :--- | :--- |
| **Orchestrator** | 🌪️ **Apache Airflow** | ควบคุม Workflow และจัดการ Task Dependencies |
| **Storage** | 🗄️ **MinIO** | Object Storage (S3 API) สำหรับเก็บ Raw Data & Parquet |
| **Processing** | 🐼 **Pandas / DuckDB** | แปลงข้อมูล (Transform) และจัดทำ Aggregation |
| **Validation** | 🚦 **Pandera** | ตรวจสอบ Schema และ Data Integrity |
| **Serving** | 🔌 **Flask API** | REST Endpoint สำหรับส่งข้อมูล JSON |
| **Frontend** | 🖥️ **Streamlit** | Visualization Dashboard สำหรับ User |

---

## 📂 Repository Map

โครงสร้างไฟล์ภายในโปรเจกต์:

```text
.
├── dags/               # Airflow Scripts (ETL Logic definition)
├── data/               # Local Storage Mapping (Simulated Data Lake)
├── docker-compose.yaml # Infrastructure Configuration
├── dashboard.py        # Streamlit Application
├── api.py              # Backend Service
└── requirements.txt    # Project Dependencies
