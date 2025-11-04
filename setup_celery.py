"""
Quick Setup Script for Windows
Installs required packages for Celery message queue system
"""
import subprocess
import sys

def install_packages():
    """Install required Python packages"""
    print("=" * 70)
    print("Installing required packages...")
    print("=" * 70)
    print()
    
    packages = [
        'celery',
        'redis',
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True


def check_redis_installed():
    """Check if Redis is available"""
    print("\n" + "=" * 70)
    print("Checking Redis installation...")
    print("=" * 70)
    print()
    
    try:
        import redis
        print("✅ Redis Python package is installed")
        
        # Try to connect
        try:
            r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
            r.ping()
            print("✅ Redis server is running and accessible")
            return True
        except redis.ConnectionError:
            print("⚠️  Redis Python package installed, but Redis server not running")
            print("\nRedis Server Options:")
            print("=" * 70)
            print("\nOption 1: Use Docker (Easiest)")
            print("  docker run -d -p 6379:6379 redis:latest")
            print()
            print("Option 2: Install Redis for Windows")
            print("  1. Download from: https://github.com/microsoftarchive/redis/releases")
            print("  2. Install Redis")
            print("  3. Run: redis-server")
            print()
            print("Option 3: Use WSL (Windows Subsystem for Linux)")
            print("  wsl")
            print("  sudo apt-get update")
            print("  sudo apt-get install redis-server")
            print("  redis-server")
            print()
            print("Option 4: Use Memurai (Redis alternative for Windows)")
            print("  Download from: https://www.memurai.com/")
            print()
            return False
            
    except ImportError:
        print("❌ Redis Python package not installed")
        return False


def main():
    print("\n" + "=" * 70)
    print("CELERY MESSAGE QUEUE - SETUP FOR WINDOWS")
    print("=" * 70)
    print()
    
    # Step 1: Install packages
    print("Step 1: Installing Python packages")
    if not install_packages():
        print("\n❌ Failed to install packages. Please try manually:")
        print("  pip install celery redis")
        return
    
    # Step 2: Check Redis
    print("\nStep 2: Checking Redis server")
    redis_ok = check_redis_installed()
    
    # Summary
    print("\n" + "=" * 70)
    print("SETUP SUMMARY")
    print("=" * 70)
    
    if redis_ok:
        print("\n✅ Everything is ready!")
        print("\nNext steps:")
        print("  1. Start Celery worker: python start_celery_worker.py")
        print("  2. Start API server: python run.py")
        print("  3. Test system: python test_celery_system.py")
    else:
        print("\n⚠️  Setup incomplete - Redis server not running")
        print("\nYou need to:")
        print("  1. Install and start Redis server (see options above)")
        print("  2. Then start Celery worker: python start_celery_worker.py")
        print("  3. Then start API server: python run.py")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
