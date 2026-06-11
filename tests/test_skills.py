from __future__ import annotations

from pathlib import Path

import pytest

from cscode.skills.loader import Skill, SkillLoader


class TestSkillLoader:
    async def test_load_skill_from_file(self, tmp_path: Path):
        skill_file = tmp_path / "test-skill.md"
        skill_file.write_text("""# Test Skill

## Description
A test skill for verifying the loader.

## Usage
```bash
echo "hello"
```

## Steps
1. Step one
2. Step two
""")
        loader = SkillLoader()
        skill = await loader.load_skill(str(skill_file))
        assert skill is not None
        assert skill.name == "Test Skill"
        assert "Test Skill" in skill.content
        assert skill.slug == "test-skill"

    async def test_load_nonexistent_skill(self):
        loader = SkillLoader()
        skill = await loader.load_skill("/nonexistent/skill.md")
        assert skill is None

    async def test_discover_skills(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a.md").write_text("# Skill A\n\n## Description\nFirst")
        (skills_dir / "skill-b.md").write_text("# Skill B\n\n## Description\nSecond")

        loader = SkillLoader()
        skills = await loader.discover(str(skills_dir))
        assert len(skills) >= 2
        names = [s.slug for s in skills]
        assert "skill-a" in names
        assert "skill-b" in names

    async def test_skill_extract_metadata(self, tmp_path: Path):
        skill_file = tmp_path / "review.md"
        skill_file.write_text("""# Code Review Skill

## Description
Review code for bugs and style issues.

## Triggers
- review my code
- check for bugs

## Steps
1. Read the diff
2. Analyze for issues
3. Generate report
""")
        loader = SkillLoader()
        skill = await loader.load_skill(str(skill_file))
        assert skill is not None
        assert skill.slug == "review"
        assert "triggers" in skill.content.lower()
