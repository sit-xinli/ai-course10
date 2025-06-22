from metagpt.roles import (
 ProjectManager,
 ProductManager,
 Architect,
 Engineer
)
from metagpt.team import Team
import asyncio

async def main():
    # Define the project requirement
    requirement = "Create a web application that allows users to search for and compare AI agent frameworks"
    
    # Create team members with different roles
    product_manager = ProductManager()
    project_manager = ProjectManager()
    architect = Architect()
    engineer = Engineer()
    
    # Form a team with these roles
    team = Team(
        name="AI Framework Explorer Team",
        members=[product_manager, project_manager, architect, engineer]
    )
    
    # Start the team working on the requirement
    await team.run(requirement)
    
    # The team will generate:
    # 1. PRD (Product Requirements Document)
    # 2. Design documents
    # 3. Architecture diagrams
    # 4. Implementation code
    # 5. Tests
if __name__ == "__main__":
    asyncio.run(main())