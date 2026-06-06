from pmle.stance_store import StanceStore
from pmle.data.cached_stances import CACHED

def main():
    store = StanceStore()
    for s in CACHED:
        store.set(s.stakeholder, s)
    print(f"Seeded {len(CACHED)} stances into pmle_stances.db")

if __name__ == "__main__":
    main()
