import os
import stripe
import psycopg2
from fastapi import FastAPI, Request, Header, HTTPException

app = FastAPI()

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]
DATABASE_URL = os.environ["DATABASE_URL"]

def db_exec(query, params=()):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
    finally:
        conn.close()

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] in ["customer.subscription.created", "customer.subscription.updated"]:
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        status = sub["status"]  # active, canceled, past_due...

        our_status = "active" if status == "active" else ("canceled" if status == "canceled" else "past_due")

        db_exec(
            "update subscriptions set stripe_subscription_id=%s, status=%s, updated_at=now() where stripe_customer_id=%s",
            (sub["id"], our_status, customer_id),
        )

    return {"ok": True}
