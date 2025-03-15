import os
import re
import json
from difflib import unified_diff

# Import the dependency analyzer (Ensure the corresponding module is available)
from dependency_analysis import DependencyAnalyzer  


class RAGEditPool:
    """
    A class to manage and rank code edit fragments using dependency analysis.

    Attributes
    ----------
    max_lines : int
        The maximum number of lines per edit fragment.
    edit_pool : list
        A list storing edit fragments.
    dependency_analyzer : DependencyAnalyzer
        An instance of the dependency analyzer to calculate dependencies.
    """

    def __init__(self, max_lines=15):
        """
        Initialize the RAG Edit Pool.

        Parameters
        ----------
        max_lines : int, optional
            The maximum number of lines per edit fragment, default is 15.
        """
        self.max_lines = max_lines
        self.edit_pool = []
        self.dependency_analyzer = DependencyAnalyzer()

    def add_edit(self, before_edit, after_edit):
        """
        Add a new edit to the pool by splitting it into fragments.

        Parameters
        ----------
        before_edit : str
            The function signature and body before modification.
        after_edit : str
            The function signature and body after modification.

        Returns
        -------
        None
        """
        before_lines = before_edit.splitlines()
        after_lines = after_edit.splitlines()
        diff = list(unified_diff(before_lines, after_lines, lineterm=""))

        chunk = []
        for line in diff:
            chunk.append(line)
            if len(chunk) == self.max_lines:
                self.edit_pool.append("\n".join(chunk))
                chunk = []

        if chunk:
            self.edit_pool.append("\n".join(chunk))

    def add_edit_from_patch(self, patch):
        """
        Add an edit to the pool based on a patch string.

        Parameters
        ----------
        patch : str
            The patch string containing the edit information.

        Returns
        -------
        None
        """
        before_edit, after_edit = self._parse_patch(patch)
        self.add_edit(before_edit, after_edit)

    def _parse_patch(self, patch):
        """
        Parse the patch string to extract before and after code.

        Parameters
        ----------
        patch : str
            The patch string containing the edit information.

        Returns
        -------
        tuple
            A tuple (before_edit, after_edit) strings.
        """
        before_edit, after_edit = [], []
        lines = patch.splitlines()

        for line in lines:
            if line.startswith('-'):
                before_edit.append(line[1:])  
            elif line.startswith('+'):
                after_edit.append(line[1:])  
            elif line.startswith('@@'):
                continue  
            else:
                before_edit.append(line)
                after_edit.append(line)

        return "\n".join(before_edit), "\n".join(after_edit)

    def calculate_dependency_scores(self, reference_code):
        """
        Calculate dependency scores for all fragments in the pool.

        Parameters
        ----------
        reference_code : str
            The reference code string to compare against.

        Returns
        -------
        list
            A list of tuples (fragment, dependency_score), sorted in descending order.
        """
        scores = [
            (fragment, self.dependency_analyzer.get_dependency(reference_code, fragment))
            for fragment in self.edit_pool
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def get_top_k_fragments(self, reference_code, k):
        """
        Get the top K fragments with the highest dependency scores.

        Parameters
        ----------
        reference_code : str
            The reference code string to compare against.
        k : int
            The number of top fragments to return.

        Returns
        -------
        list
            A list of tuples (fragment, dependency_score).
        """
        sorted_scores = self.calculate_dependency_scores(reference_code)
        return sorted_scores[:min(k, len(sorted_scores))]

    def get_fragments_in_range(self, reference_code, l, r):
        """
        Get fragments ranked between positions l and r (inclusive).

        Parameters
        ----------
        reference_code : str
            The reference code string to compare against.
        l : int
            The starting rank (1-based, inclusive).
        r : int
            The ending rank (1-based, inclusive).

        Returns
        -------
        list
            A list of tuples (fragment, dependency_score).
        """
        if l <= 0 or r <= 0 or l > r or l > len(self.edit_pool):
            return []
        sorted_scores = self.calculate_dependency_scores(reference_code)
        return sorted_scores[l - 1 : min(r, len(sorted_scores))]

    def export_edit_pool(self, file_path="edit_pool.json"):
        """
        Save the edit pool to a JSON file.

        Parameters
        ----------
        file_path : str, optional
            The file path to save the edit pool, default is "edit_pool.json".

        Returns
        -------
        None
        """
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.edit_pool, file, indent=4)

    def load_edit_pool(self, file_path="edit_pool.json"):
        """
        Load the edit pool from a JSON file.

        Parameters
        ----------
        file_path : str, optional
            The file path to load the edit pool, default is "edit_pool.json".

        Returns
        -------
        None
        """
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                self.edit_pool = json.load(file)

    def clear_edit_pool(self):
        """
        Clear all edit fragments from the pool.

        Returns
        -------
        None
        """
        self.edit_pool = []

    def __len__(self):
        """
        Return the number of fragments in the edit pool.

        Returns
        -------
        int
        """
        return len(self.edit_pool)

    def __str__(self):
        """
        String representation of the edit pool.

        Returns
        -------
        str
        """
        return f"RAGEditPool with {len(self.edit_pool)} fragments."

    def __repr__(self):
        """
        Official string representation of the class.

        Returns
        -------
        str
        """
        return f"RAGEditPool(max_lines={self.max_lines})"


if __name__ == '__main__':
    rag_pool = RAGEditPool(max_lines=15)

    # Example edits
    rag_pool.add_edit("def add(a, b): return a + b", "def add(a, b, c): return a + b + c")
    rag_pool.add_edit("def multiply(a, b): return a * b", "def multiply(a, b, c): return a * b * c")

    print(f"Number of fragments in the pool: {len(rag_pool)}")

    reference_code = "def calculate(x, y): return x + y"
    top_k = rag_pool.get_top_k_fragments(reference_code, 10)

    print("Top K Fragments:")
    for fragment, score in top_k:
        print(f"Fragment: {fragment}, Score: {score}")
