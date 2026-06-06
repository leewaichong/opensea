PERSONAS = {
    "PM":       {"private": "Wants to ship before 11.11 for promo revenue. Assumes checkout "
                            "security means a server-side session. Will accept conditions that "
                            "don't slip the date."},
    "Backend":  {"private": "Believes checkout backend is ready. Assumes session handling is "
                            "server-side; 'secure' means the server controls the session."},
    "SRE":      {"private": "Worried about 11.11 traffic (may exceed last peak by 35%), queue "
                            "backpressure, and rollback readiness. Blocks load-readiness."},
    "Security": {"private": "Will block launch if ANY checkout token is stored client-side. "
                            "'Secure' means no client-side token at all — non-negotiable."},
}
