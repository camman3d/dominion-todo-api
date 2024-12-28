"""Seed AI Prompts

Revision ID: cf30951c9c12
Revises: ea41c71fd6b6
Create Date: 2024-12-27 10:12:57.744080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf30951c9c12'
down_revision: Union[str, None] = 'ea41c71fd6b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Get reference to ai_prompts table
    ai_prompts = sa.table(
        'ai_prompts',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String()),
        sa.Column('description', sa.String()),
        sa.Column('cost', sa.Integer()),
        sa.Column('prompt_template', sa.String()),
        sa.Column('returns_json', sa.Boolean())
    )

    # Insert seed data
    op.bulk_insert(
        ai_prompts,
        [
            {
                'name': 'Action Plan',
                'description': 'Create an Action Plan',
                'cost': 1,
                'prompt_template': '''You are a highly organized and detail-oriented assistant. Your goal is to break down the task into smaller, actionable steps and organize them into a logical sequence. 

Task: "{task_description}"

Provide a step-by-step action plan to accomplish this task effectively.

Return your response as markdown.
''',
                'returns_json': False,
            },
            {
                'name': 'Motivation',
                'description': 'Motivate Me',
                'cost': 1,
                'prompt_template': '''You are a motivational coach helping someone complete an important task. Your goal is to inspire and encourage them by highlighting the significance of the task, offering practical guidance for starting, and boosting their confidence.

Task: "{task_description}"

Provide a motivational message that includes:
1. Why this task is important or beneficial.
2. A simple first step to get started.
3. Encouraging words to help them stay focused and positive.

Return your response as markdown.
''',
                'returns_json': False,
            },
            {
                'name': 'Related Tasks',
                'description': 'Suggest Related Tasks',
                'cost': 1,
                'prompt_template': '''You are a smart assistant helping someone plan comprehensively for a task. Your goal is to suggest related or dependent tasks that will help them fully prepare or execute the primary task.

Task: "{task_description}"

Return your response as a JSON object with a list of related tasks. Each task should have a clear and concise description. Here is the required format:

{
  "tasks": [
    {"description": "Task description goes here"},
    {"description": "Second task description goes here"},
    {"description": "Third task description goes here"}
  ]
}

''',
                'returns_json': True,
            }
        ]
    )

def downgrade():
    op.execute('TRUNCATE TABLE ai_prompts')