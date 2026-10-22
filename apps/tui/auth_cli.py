import argparse
import asyncio
import getpass
import sys

from apps.tui.client import TUIClient


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="noesis-auth",
        description="Authenticate before running the Noesis TUI to skip the login page.",
    )
    parser.add_argument(
        "--email",
        "-e",
        help="Email address for login",
    )
    parser.add_argument(
        "--password",
        "-p",
        help="Password for login",
    )
    parser.add_argument(
        "--demo",
        "-d",
        action="store_true",
        help="Authenticate instantly with demo account (Alex)",
    )
    parser.add_argument(
        "--logout",
        action="store_true",
        help="Log out and clear saved authentication session",
    )
    parser.add_argument(
        "--status",
        "--whoami",
        action="store_true",
        dest="status",
        help="Display currently authenticated user",
    )
    return parser.parse_args(args)


async def async_main(args=None) -> int:
    parsed = parse_args(args)
    client = TUIClient()

    # 1. Status / Whoami
    if parsed.status:
        if client.has_saved_session():
            profile = await client.get_profile()
            print(f"✨ Currently authenticated:")
            print(f"  • Name:     {profile.get('name', 'Learner')}")
            print(f"  • Email:    {profile.get('email', 'N/A')}")
            print(f"  • Target:   {profile.get('learningLanguage', 'Spanish')} ({profile.get('currentLevel', 'A1')})")
            print(f"  • Streak:   {profile.get('streakDays', 1)} days")
            print(f"  • Total XP: {profile.get('totalXp', 0)} XP")
            print("\nSession is active. Running 'uv run noesis-tui' will skip the login screen.")
            return 0
        else:
            print("❌ Not currently authenticated.")
            print("Run 'uv run noesis-auth' or 'uv run noesis-tui login' to sign in.")
            return 1

    # 2. Logout
    if parsed.logout:
        client.logout()
        print("✅ Logged out successfully. Saved session cleared.")
        return 0

    # 3. Demo login
    if parsed.demo:
        print("⚡ Authenticating with Demo account...")
        try:
            result = await client.demo_login()
            user = result.get("user", {})
            print(f"✅ Successfully authenticated as {user.get('email', 'alex@example.com')} ({user.get('name', 'Alex')})")
            print("💾 Session saved. You can now run 'uv run noesis-tui' to open directly to the dashboard!")
            return 0
        except Exception as e:
            print(f"❌ Demo login failed: {e}")
            return 1

    # 4. Email / Password (interactive or flags)
    email = parsed.email
    password = parsed.password

    if not email:
        try:
            email = input("Email address: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return 1

    if not password:
        try:
            password = getpass.getpass("Password: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return 1

    if not email or not password:
        print("❌ Both email and password are required.")
        return 1

    print(f"Authenticating as {email}...")
    try:
        result = await client.login(email, password)
        user = result.get("user", {})
        print(f"✅ Successfully authenticated as {user.get('email', email)} ({user.get('name', 'Learner')})")
        print(f"🎯 Target Language: {user.get('learningLanguage', 'Spanish')} {user.get('currentLevel', 'A1')}")
        print("💾 Session saved. You can now run 'uv run noesis-tui' to open directly to the dashboard!")
        return 0
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return 1


def main(args=None):
    """Entry point for noesis-auth CLI."""
    exit_code = asyncio.run(async_main(args))
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
