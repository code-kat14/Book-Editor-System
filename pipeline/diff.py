from diff_match_patch import diff_match_patch

dmp = diff_match_patch()
dmp.Diff_Timeout = 1.0

def word_diff(a: str, b: str):
    diffs = dmp.diff_main(a, b)
    dmp.diff_cleanupSemantic(diffs)
    return diffs  # list of (op, text)
