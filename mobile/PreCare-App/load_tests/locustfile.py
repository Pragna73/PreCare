import random
from locust import HttpUser, task, between


class PreCareUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # Sample health check on session start
        self.client.get("/", name="[Health] Root API Check")

    @task(3)
    def test_maya_chat_load(self):
        """Simulate high volume user queries to Maya AI Assistant."""
        questions = [
            "What type of excersices can u suggest me in week 32",
            "Can I travel in 32 week",
            "What should I pack in my hospital bag",
            "Is papaya safe to eat in pregnancy",
            "How many kicks should I feel in 2 hours",
            "How to relieve acidity and heartburn"
        ]
        q = random.choice(questions)
        payload = {
            "user_id": 1,
            "message": q
        }
        self.client.post(
            "/maya/chat",
            json=payload,
            name="[Maya] Maternal Q&A Chat Endpoint"
        )

    @task(2)
    def test_dashboard_summary_load(self):
        """Simulate frequent mobile dashboard vitals & risk polling."""
        self.client.get(
            "/dashboard/summary?user_id=1",
            name="[Dashboard] Summary & Risk Evaluation"
        )

    @task(1)
    def test_doctor_appointments_load(self):
        """Simulate querying prenatal doctor appointment schedules."""
        self.client.get(
            "/appointments?user_id=1",
            name="[Care] Doctor Appointments Schedule"
        )
