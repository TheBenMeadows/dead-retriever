# Pre-submission checks for the paper in paper/; targets and options are
# described in tools/paper-checks/paper-checks.mk. Build output goes to
# paper/build/, which ignores itself.
PAPER_DIR := paper
PAPER_CHECKS := tools/paper-checks
.DEFAULT_GOAL := paper-checks
include $(PAPER_CHECKS)/paper-checks.mk
