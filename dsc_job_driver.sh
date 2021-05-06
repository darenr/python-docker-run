prepare_driver() {
cat <<EOF > oci_driver.py
import os
import json
import importlib
import sys

import git
import os


class GitManager:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.code_dir = os.environ.get("CODE_DIR", "/app/code")

    def fetch_repo(self):
        self.repo = git.Repo.clone_from(self.repo_url, self.code_dir)
        print(f"Cloned at: {os.listdir(self.code_dir)}")
        return self

    def setup_code(self, branch=None, commit=None):
        if commit:
            print(f"Checking out commit: {commit}")
            self.repo.git.checkout(commit)
        else:
            print(f"Pointing to the latest commit")
            print(
                "Repo Details:", self.repo, self.repo_url, self.repo.head.commit.hexsha
            )
        self.commit = self.repo.head.commit.hexsha
        return self

    def code_git_metadata(self):
        """code_git_metadata."""
        return {"repo": self.repo_url, "commit": self.commit}


def setup_python_path(code_dir):
    PATH = os.path.join(code_dir)
    print(f"Setting up python path: {PATH}")
    print(f"found: {os.listdir(PATH)}")
    sys.path.append(PATH)


def run(params={}):

    gm = (
        GitManager(os.environ.get("GIT_URL"))
        .fetch_repo()
        .setup_code(
            branch=os.environ.get("BRANCH", None), commit=os.environ.get("COMMIT", None)
        )
    )

    setup_python_path(gm.code_dir)
    module = importlib.import_module(f"{os.environ.get('ENTRY_SCRIPT')}")
    method = getattr(module, os.environ.get("ENTRY_FUNCTION", "__main__"))
    method(**params)


def main():
    params = json.loads(os.environ.get("PARAMS", "{}"))
    run(params)


if __name__ == "__main__":
    main()

EOF
}


rm -rf /home/datascience/app/code && \
rm -rf /home/datascience/conda/runenvv1_0 && \
echo | odsc conda install -s $SLUG -e runenv && \
conda init bash && \
source ~/.bashrc && \
conda activate /home/datascience/conda/runenvv1_0 && \
prepare_driver && \
python oci_driver.py
