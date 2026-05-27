import os
import subprocess

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def main():
    print("="*60)
    print("GitHub Repository Push Assistant")
    print("="*60)
    print("This script will help you link and push this local project to your GitHub.")
    print("Please make sure you have already created a public repository on github.com.")
    print("="*60)
    
    repo_url = input("\n👉 Paste your GitHub repository URL (e.g., https://github.com/username/repo.git): ").strip()
    if not repo_url:
        print("❌ Error: Repository URL cannot be empty.")
        return
        
    # Ensure it ends with .git if it's HTTPS
    if repo_url.startswith("http") and not repo_url.endswith(".git"):
        repo_url += ".git"
        
    print("\n1. Renaming local branch to 'main'...")
    run_cmd("git branch -M main")
    
    print("2. Configuring remote 'origin'...")
    # Remove existing remote if it exists
    run_cmd("git remote remove origin")
    code, out, err = run_cmd(f"git remote add origin {repo_url}")
    if code != 0:
        print(f"❌ Error setting remote: {err}")
        return
        
    print(f"✅ Linked remote 'origin' to: {repo_url}")
    
    print("\n3. Pushing local repository to GitHub...")
    print("⚠️  A Windows GitHub Credential Manager popup or console prompt will appear.")
    print("👉 Please log in or paste your GitHub Personal Access Token (PAT) to complete authentication.")
    print("Running command: git push -u origin main...\n")
    
    # We run push with interactive stdout/stderr so the user can see credential prompts
    try:
        subprocess.run("git push -u origin main", shell=True, check=True)
        print("\n🎉 Success! Your code is now live on your GitHub repository!")
    except subprocess.CalledProcessError:
        print("\n❌ Error: Failed to push to repository. Make sure you entered the correct credentials.")
        print("💡 If you don't have Git configured with your credentials, try installing GitHub Desktop or setting up a Personal Access Token (PAT).")

if __name__ == "__main__":
    main()
