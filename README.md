# 🚀 Real-Time Collaborative Document Editor

A distributed, production-grade collaborative editor powered by **FastAPI**, **Redis**, **PostgreSQL**, and a custom **Operational Transformation (OT)** engine.

## 🧠 The Architecture

This project uses a distributed system architecture to ensure that multiple users can edit the same document simultaneously across different server instances.

```mermaid
graph TD
    subgraph Clients
        UA[💻 User A]
        UB[💻 User B]
    end

    subgraph "Application Layer (FastAPI Instances)"
        S1[⚙️ Server Instance 1]
        S2[⚙️ Server Instance 2]
    end

    subgraph "State & Communication"
        Redis[(📡 Redis Pub/Sub Bus)]
        DB[(🐘 PostgreSQL DB)]
    end

    UA <-->|WebSockets| S1
    UB <-->|WebSockets| S2
    
    S1 <--> Redis
    S2 <--> Redis
    
    S1 -->|Event Logging| DB
    S2 -->|Event Logging| DB
```

### The Operational Flow

```mermaid
sequenceDiagram
    participant UserA as 💻 User A (Tab 1)
    participant Srv1 as ⚙️ Server Instance 1
    participant Redis as 📡 Redis Pub/Sub (The Bus)
    participant DB as 🐘 PostgreSQL (Source of Truth)
    participant Srv2 as ⚙️ Server Instance 2
    participant UserB as 💻 User B (Tab 2)

    UserA->>Srv1: Sends Operation (Insert 'X' at Pos 5)
    Note over Srv1: OT ENGINE:<br/>Transform against missed history
    Srv1->>DB: Save Transformed Operation (Revision 12)
    Srv1->>Redis: Publish Operation to Document Channel
    Redis-->>Srv1: Broadcast back to local clients
    Redis-->>Srv2: Broadcast to remote server instances
    Srv1->>UserA: Sync Confirmation
    Srv2->>UserB: Push Real-Time Update via WebSocket
    Note over UserB: Client-Side OT:<br/>Shift local cursor if needed
```

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI (Asynchronous WebSockets)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Message Bus**: Redis (Distributed Pub/Sub for horizontal scaling)
- **Algorithm**: Operational Transformation (Character-based conflict resolution)
- **Frontend**: Vanilla JS with Optimistic UI & Client-side Transformation

## 💎 Core Features

### 1. Distributed Operational Transformation
Most editors break when two people type at the same time. This engine calculates the "Index Shift" required to keep both users in sync, even if their messages arrive out of order.

### 2. Event Sourcing
Instead of saving document snapshots, we save every single keystroke. This allows for:
- **Infinite Undo/Redo** (Potential feature)
- **Time Travel**: Replaying the document history to any point in time.
- **Perfect Conflict Resolution**.

### 3. Horizontal Scalability
By using Redis as a message bus, you can run 100 instances of this server behind a Load Balancer, and users on Server A will see updates from users on Server B instantly.

## 🚀 Getting Started

1. **Setup Database**:
   ```bash
   # Make sure PostgreSQL and Redis are running
   alembic upgrade head
   ```

2. **Run Server**:
   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```

3. **Open Client**:
   Simply open `index.html` in your browser. Open multiple tabs to see the OT magic in action!

---
*Built with ❤️ and Hard Engineering.*
