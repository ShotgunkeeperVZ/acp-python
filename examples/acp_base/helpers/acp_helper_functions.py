import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from acp_sdk.client import VirtualsACP
from acp_sdk.configs import BASE_SEPOLIA_CONFIG
from acp_sdk.env import EnvSettings

from dotenv import load_dotenv

load_dotenv(override=True)


def test_helper_functions():
    env = EnvSettings()
            
    acp = VirtualsACP(
        wallet_private_key=env.WHITELISTED_WALLET_PRIVATE_KEY,
        agent_wallet_address=env.BUYER_WALLET_ADDRESS,
        config=BASE_SEPOLIA_CONFIG
    )
    
    # Get active jobs
    active_jobs = acp.get_active_jobs(page=1, pageSize=10)
    print("\n🔵 Active Jobs:")
    print(active_jobs or "No active jobs found.")

    # Get completed jobs
    completed_jobs = acp.get_completed_jobs(page=1, pageSize=10)
    print("\n✅ Completed Jobs:")
    print(completed_jobs or "No completed jobs found.")

    # Get cancelled jobs
    cancelled_jobs = acp.get_cancelled_jobs(page=1, pageSize=10)
    print("\n❌ Cancelled Jobs:")
    print(cancelled_jobs or "No cancelled jobs found.")

    if completed_jobs:
        onchain_job_id = completed_jobs[0].get("id")
        if onchain_job_id:
            job = acp.get_job_by_onchain_id(onchain_job_id=onchain_job_id)
            print(f"\n📄 Job Details (Job ID: {onchain_job_id}):")
            print(job)

        memos = completed_jobs[0].get("memos", [])
        if memos:
            memo_id = memos[0].get("id")
            memo = acp.get_memo_by_id(onchain_job_id=onchain_job_id, memo_id=memo_id)
            print(f"\n📝 Memo Details (Job ID: {onchain_job_id}, Memo ID: {memo_id}):")
            print(memo)
        else:
            print("\n⚠️ No memos found for the completed job.")
    else:
        print("\n⚠️ No completed jobs available for detailed inspection.")


if __name__ == "__main__":
    test_helper_functions()
