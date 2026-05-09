# Release Process

This document explains how this project creates software releases using GitHub Actions.

It is intentionally detailed so that someone can come back months or years later and understand:

- what the release workflows do
- when to use each workflow
- how version numbers are chosen
- how to decide between major, minor, patch, or no release
- how to troubleshoot common problems

The goal is not to make releases fully automatic. The goal is to make releases easier, more consistent, and less error-prone while still keeping the final decision human-approved.

---

# 1. Plain-English Summary

This project uses two GitHub Actions workflows:

```text
1 - Suggest Release Version
2 - Create Release
