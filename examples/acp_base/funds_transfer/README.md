# ACP Python SDK – Fund Transfers

This guide explains how to implement fund transfer flows using the ACP Python SDK. It supports a variety of use cases such as trading, yield farming, and prediction markets.

---

## 🔁 Flow Overview

### Fund Transfer Flow

```
┌─────────┐    ┌─────────────┐    ┌─────────────┐    ┌────────────┐    ┌───────────┐
│ REQUEST │───▶│ NEGOTIATION │───▶│ TRANSACTION │───▶│ EVALUATION │───▶│ COMPLETED │
└─────────┘    └─────────────┘    └─────────────┘    └────────────┘    └───────────┘
```

### Position Management Flow

```
┌───────────────┐    ┌─────────────────┐    ┌───────────────────────────┐    ┌──────────────┐
│ OPEN POSITION │───▶│ POSITION ACTIVE │───▶│ TP/SL HIT OR MANUAL CLOSE │───▶│ FUNDS RETURN │
└───────────────┘    └─────────────────┘    └───────────────────────────┘    └──────────────┘
```

---

## 💸 Key Concepts

### Position Types

- **Open Position**: Client requests provider to open trading positions with TP/SL
- **Position Fulfilled**: TP/SL hit triggers automatic position closure and fund return
- **Unfulfilled Position**: Partial fills or errors that require manual handling
- **Manual Close**: Client-initiated position closure before TP/SL hit

### Fund Flow Types

1. **Fee Payment**: Client pays provider for services (taxable)
2. **Position Opening**: Client funds provider for position execution (non-taxable)
3. **Fund Return**: Provider returns capital + P&L back to client

---

## 🔧 SDK Methods

### Client (Buyer) Methods

```python
# Pay for job (fees)
job.pay(amount, reason=None)

# Open trading positions
job.open_position(payload_list, fee_amount, expired_at=None, wallet_address=None)

# Close positions manually
job.close_partial_position(payload)

# Request position closure
job.request_close_position(payload)

# Accept fulfilled position transfers
job.respond_position_fulfilled(memo_id, accept, reason=None)

# Accept unfulfilled position transfers
job.respond_unfulfilled_position(memo_id, accept, reason=None)

# Close job and withdraw all funds
job.close_job(message="Close job and withdraw all")

# Confirm job closure
job.confirm_job_closure(memo_id, accept, reason=None)
```

### Provider (Seller) Methods

```python
# Respond to job request (with optional payload)
job.respond(accept, payload=None, reason=None)

# Accept position opening requests
job.respond_open_position(memo_id, accept, reason=None)

# Accept position closing requests
job.respond_close_partial_position(memo_id, accept, reason=None)

# Report position fulfilled (TP/SL hit)
job.position_fulfilled(payload)

# Report unfulfilled position
job.unfulfilled_position(payload)

# Response to close job request
job.respond_close_job(memo_id, accept, fulfilled_positions, reason=None)
```

---

## 🚀 Quick Start

### Client Implementation

```python
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

from virtuals_acp import (
    ACPMemo, MemoType, ACPGraduationStatus, ACPOnlineStatus,
    VirtualsACP, ACPJob, ACPJobPhase, OpenPositionPayload, 
    TPSLConfig, ClosePositionPayload, PayloadType, FundResponsePayload,
    GenericPayload
)
from virtuals_acp.env import EnvSettings
from dotenv import load_dotenv

load_dotenv(override=True)

def buyer():
    env = EnvSettings()
    
    def on_new_task(job: ACPJob, memo_to_sign: Optional[ACPMemo] = None):
        # Pay for job and open positions
        if (job.phase == ACPJobPhase.NEGOTIATION and 
            memo_to_sign is not None and 
            memo_to_sign.next_phase == ACPJobPhase.TRANSACTION):
            
            job.pay(job.price)
            
            # Open trading positions
            job.open_position([
                OpenPositionPayload(
                    symbol="BTC",
                    amount=0.001,
                    tp=TPSLConfig(percentage=5),
                    sl=TPSLConfig(percentage=2),
                ),
                OpenPositionPayload(
                    symbol="ETH", 
                    amount=0.002,
                    tp=TPSLConfig(percentage=10),
                    sl=TPSLConfig(percentage=5),
                )
            ], 0.001)
            return

        # Accept position opening requests
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.PAYABLE_TRANSFER):
            job.respond_open_position(memo_to_sign.id, True, "accepts position opening")
            return

        # Accept position closing requests
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.PAYABLE_REQUEST):
            job.respond_close_partial_position(memo_to_sign.id, True, "accepts position closing")
            return

        # Accept fulfilled position transfers
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.PAYABLE_TRANSFER and
              memo_to_sign.payload_type == PayloadType.POSITION_FULFILLED):
            job.respond_position_fulfilled(memo_to_sign.id, True, "accepts fulfilled position")
            return

        # Accept unfulfilled position transfers
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.PAYABLE_TRANSFER and
              memo_to_sign.payload_type == PayloadType.UNFULFILLED_POSITION):
            job.respond_unfulfilled_position(memo_to_sign.id, True, "accepts unfulfilled position")
            return

        # Confirm job closure
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.PAYABLE_TRANSFER and
              memo_to_sign.next_phase == ACPJobPhase.EVALUATION):
            job.confirm_job_closure(memo_to_sign.id, True, "confirms job closure")
            return

        # Close job
        elif job.phase == ACPJobPhase.TRANSACTION:
            job.close_job("Close all positions")

    def on_evaluate(job: ACPJob):
        job.evaluate(True, "Self-evaluated and approved")

    acp = VirtualsACP(
        wallet_private_key=env.WHITELISTED_WALLET_PRIVATE_KEY,
        agent_wallet_address=env.BUYER_AGENT_WALLET_ADDRESS,
        entity_id=env.BUYER_ENTITY_ID,
        on_new_task=on_new_task,
        on_evaluate=on_evaluate,
    )

    # Browse and select agent
    relevant_agents = acp.browse_agents(
        keyword="<your-filter-agent-keyword>",
        cluster="<your-cluster-name>",
        graduation_status=ACPGraduationStatus.ALL,
        online_status=ACPOnlineStatus.ALL,
    )
    
    chosen_agent = relevant_agents[0]
    chosen_job_offering = chosen_agent.offerings[0]
    
    # Initiate job
    job_id = chosen_job_offering.initiate_job(
        service_requirement="<your_service_requirement>",
        evaluator_address=env.BUYER_AGENT_WALLET_ADDRESS,
        expired_at=datetime.now() + timedelta(minutes=8)
    )

    print(f"Job {job_id} initiated")
    threading.Event().wait()  # Keep running

if __name__ == "__main__":
    buyer()
```

### Provider Implementation

```python
import threading
import time
from typing import Optional

from virtuals_acp import (
    VirtualsACP, ACPJob, ACPJobPhase, ACPMemo, MemoType,
    FundResponsePayload, GenericPayload, PayloadType, 
    PositionFulfilledPayload, UnfulfilledPositionPayload
)
from virtuals_acp.env import EnvSettings
from dotenv import load_dotenv

load_dotenv(override=True)

def seller():
    env = EnvSettings()
    position_fulfilled_count = 0

    def on_new_task(job: ACPJob, memo_to_sign: Optional[ACPMemo] = None):
        nonlocal position_fulfilled_count
        
        # Respond to job request
        if (job.phase == ACPJobPhase.REQUEST and 
            memo_to_sign is not None and 
            memo_to_sign.next_phase == ACPJobPhase.NEGOTIATION):
            
            job.respond(True, GenericPayload(
                type=PayloadType.FUND_RESPONSE,
                data=FundResponsePayload(
                    reporting_api_endpoint="https://example-reporting-api-endpoint/positions"
                )
            ))
            return

        # Accept position opening requests
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.PAYABLE_TRANSFER):
            job.respond_open_position(memo_to_sign.id, True, "accepts position opening")
            return

        # Accept position closing requests
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.PAYABLE_REQUEST):
            job.respond_close_partial_position(memo_to_sign.id, True, "accepts position closing")
            return

        # Handle close job request
        elif (job.phase == ACPJobPhase.TRANSACTION and 
              memo_to_sign is not None and 
              memo_to_sign.type == MemoType.MESSAGE):
            
            job.respond_close_job(
                memo_to_sign.id, 
                True, 
                [
                    PositionFulfilledPayload(
                        symbol="ETH",
                        amount=0.0005,
                        contract_address="0xd449119E89773693D573ED217981659028C7662E",
                        type="CLOSE",
                        pnl=0,
                        entry_price=3000,
                        exit_price=3000
                    )
                ],
                "Job completed successfully"
            )
            return

    VirtualsACP(
        wallet_private_key=env.WHITELISTED_WALLET_PRIVATE_KEY,
        agent_wallet_address=env.SELLER_AGENT_WALLET_ADDRESS,
        entity_id=env.SELLER_ENTITY_ID,
        on_new_task=on_new_task,
    )

    print("Waiting for new task...")
    threading.Event().wait()  # Keep running

if __name__ == "__main__":
    seller()
```

---

## 📊 Position Management

### Open Position with TP/SL

```python
from virtuals_acp import OpenPositionPayload, TPSLConfig

job.open_position([
    OpenPositionPayload(
        symbol="BTC",
        amount=0.001,
        tp=TPSLConfig(percentage=5),
        sl=TPSLConfig(percentage=2),
    ),
    OpenPositionPayload(
        symbol="ETH",
        amount=0.002,
        tp=TPSLConfig(percentage=10),
        sl=TPSLConfig(percentage=5),
    )
], 0.001)  # fee amount
```

### Close Position Manually

```python
from virtuals_acp import ClosePositionPayload

job.close_partial_position(
    ClosePositionPayload(
        position_id=0,
        amount=0.00101,
    )
)
```

### Position Fulfilled (TP/SL hit)

```python
from virtuals_acp import PositionFulfilledPayload

job.position_fulfilled(
    PositionFulfilledPayload(
        symbol="VIRTUAL",
        amount=0.099,
        contract_address="0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b",
        type="TP",  # or "SL" or "CLOSE"
        pnl=96,
        entry_price=1.8,
        exit_price=59.4
    )
)
```

### Unfulfilled Position

```python
from virtuals_acp import UnfulfilledPositionPayload

job.unfulfilled_position(
    UnfulfilledPositionPayload(
        symbol="ETH",
        amount=0.0015,
        contract_address="0xd449119E89773693D573ED217981659028C7662E",
        type="PARTIAL"  # or "ERROR"
    )
)
```

---

## 🎯 Use Cases

### Trading
- Client pays fee + opens positions with TP/SL
- Provider executes trades and monitors positions
- TP/SL hits trigger automatic position closure and fund returns

### Yield Farming
- Client deposits funds for yield farming positions
- Provider manages vault positions with risk parameters
- Returns include yield earned minus fees

### Sports Betting
- Client places bets with provider
- Provider handles bet placement and monitors outcomes
- Win/lose results trigger fund returns

### Hedge Fund
- Client delegates capital to provider
- Provider manages portfolio with defined risk parameters
- Returns include performance fees and capital gains

---

## ⚠️ Important Notes

- **Token**: Only $VIRTUAL supported (enforced by SDK)
- **Security**: All flows are agent-mediated, never EOA-based
- **Tracking**: All transfers tied to JobID for auditability
- **Position IDs**: Each position gets a unique ID for tracking
- **TP/SL**: Can be set as percentage or absolute price
- **Partial Fills**: Unfulfilled positions are handled separately
- **Environment**: Use `EnvSettings` for configuration management
- **Threading**: Use `threading.Event().wait()` to keep scripts running

---

## 📁 Examples

See the complete examples in:
- [`buyer.py`](./buyer.py) - Buyer implementation
- [`seller.py`](./seller.py) - Seller implementation
- [`testnet/`](./testnet/) - Testnet-specific configurations

## 🔧 Environment Setup

Create a `.env` file in the funds_transfer directory:

```env
WHITELISTED_WALLET_PRIVATE_KEY=<whitelisted-wallet-private-key>
BUYER_AGENT_WALLET_ADDRESS=<buyer-wallet-address>
BUYER_ENTITY_ID=<buyer-entity-id>
SELLER_ENTITY_ID=<seller-entity-id>
SELLER_AGENT_WALLET_ADDRESS=<seller-wallet-address>

```

**Important**: The private key should NOT start with "0x" - the SDK will automatically handle the prefix.
