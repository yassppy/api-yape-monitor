-- Stores payment notifications received by Yape Monitor.

CREATE TABLE IF NOT EXISTS payments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    sender_name VARCHAR(200) NOT NULL,

    amount NUMERIC(12, 2) NOT NULL
        CHECK (amount > 0),

    currency VARCHAR(3) NOT NULL DEFAULT 'PEN',

    payment_datetime TIMESTAMPTZ NOT NULL,

    -- Optional technical identifier from the Android notification.
    -- It must be stable enough to identify the same event.
    notification_key VARCHAR(255),

    device_name VARCHAR(100),

    -- Means the notification was stored, not independently
    -- confirmed by Yape.
    status VARCHAR(20) NOT NULL DEFAULT 'RECIBIDO'
        CHECK (status IN ('RECIBIDO', 'OBSERVADO')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Allows efficient searches by sender and payment time.
CREATE INDEX IF NOT EXISTS idx_payments_sender_datetime
    ON payments (LOWER(sender_name), payment_datetime DESC);

-- Prevents duplicate inserts when a stable notification key
-- is supplied. Multiple NULL values remain allowed.
CREATE UNIQUE INDEX IF NOT EXISTS uq_payments_notification_key
    ON payments (notification_key)
    WHERE notification_key IS NOT NULL;
