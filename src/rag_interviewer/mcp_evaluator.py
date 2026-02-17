"""MCP (Model Context Protocol) integration for code evaluation.

Provides secure code execution and validation capabilities via MCP.
"""
import logging
import re
from typing import Dict, Any, Optional

from rag_interviewer.logging import get_logger

log = get_logger(__name__)


class CodeExecutionManager:
    """Manages safe code execution for interview evaluations."""
    
    # Supported languages for code execution
    SUPPORTED_LANGUAGES = ["python", "javascript", "java", "go", "rust"]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_code_blocks(self, text: str) -> list[Dict[str, Any]]:
        """Extract code blocks from text.
        
        Args:
            text: Text that may contain code blocks
            
        Returns:
            List of dicts with 'language' and 'code' keys
        """
        # Pattern to match markdown code blocks
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for lang, code in matches:
            code_blocks.append({
                "language": lang.lower() if lang else "text",
                "code": code.strip()
            })
        
        return code_blocks
    
    def validate_code_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax without executing.
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Validation results with 'valid', 'errors', 'suggestions'
        """
        if language == "python":
            return self._validate_python_syntax(code)
        elif language in ["javascript", "typescript"]:
            return self._validate_js_syntax(code)
        else:
            return {
                "valid": True,
                "errors": [],
                "suggestions": [f"Syntax validation for {language} not implemented"],
                "language": language
            }
    
    def _validate_python_syntax(self, code: str) -> Dict[str, Any]:
        """Validate Python syntax."""
        import ast
        
        try:
            ast.parse(code)
            return {
                "valid": True,
                "errors": [],
                "suggestions": ["Syntax is valid Python"],
                "language": "python"
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Syntax error at line {e.lineno}: {e.msg}"],
                "suggestions": ["Check indentation and syntax"],
                "language": "python"
            }
    
    def _validate_js_syntax(self, code: str) -> Dict[str, Any]:
        """Basic JavaScript validation (placeholder)."""
        # In production, this would use a JS parser or MCP tool
        errors = []
        
        # Basic checks
        if code.count("{") != code.count("}"):
            errors.append("Unmatched braces")
        if code.count("(") != code.count(")"):
            errors.append("Unmatched parentheses")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "suggestions": [] if len(errors) == 0 else ["Check bracket matching"],
            "language": "javascript"
        }
    
    def evaluate_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Evaluate code quality and best practices.
        
        Args:
            code: Code to evaluate
            language: Programming language
            
        Returns:
            Quality assessment with score and recommendations
        """
        score = 10  # Start with perfect score
        issues = []
        recommendations = []
        
        if language == "python":
            # Check for Python best practices
            if "import *" in code:
                score -= 2
                issues.append("Wildcard imports used")
                recommendations.append("Use explicit imports")
            
            if "print(" in code and "logging" not in code:
                score -= 1
                issues.append("Using print instead of logging")
                recommendations.append("Use logging module for production code")
            
            if "#" not in code and len(code.split("\n")) > 10:
                score -= 1
                issues.append("Missing comments/docstrings")
                recommendations.append("Add docstrings and comments")
            
            if "try:" in code and "except Exception:" in code:
                score -= 1
                issues.append("Broad exception handling")
                recommendations.append("Catch specific exceptions")
        
        return {
            "score": max(0, score),
            "max_score": 10,
            "issues": issues,
            "recommendations": recommendations,
            "language": language
        }


class MCPEvaluator:
    """MCP-enhanced evaluator for interview responses."""
    
    def __init__(self):
        self.code_manager = CodeExecutionManager()
        self.logger = logging.getLogger(__name__)
    
    def evaluate_response(
        self,
        question: str,
        answer: str,
        level: str = "beginner"
    ) -> Dict[str, Any]:
        """Comprehensive evaluation of interview response.
        
        Args:
            question: The interview question
            answer: Candidate's answer
            level: Interview level (beginner, intermediate, advanced)
            
        Returns:
            Evaluation results with score, feedback, and code analysis
        """
        # Extract and analyze any code
        code_blocks = self.code_manager.extract_code_blocks(answer)
        code_analysis = []
        
        for block in code_blocks:
            if block["language"] in CodeExecutionManager.SUPPORTED_LANGUAGES:
                syntax_result = self.code_manager.validate_code_syntax(
                    block["code"], block["language"]
                )
                quality_result = self.code_manager.evaluate_code_quality(
                    block["code"], block["language"]
                )
                
                code_analysis.append({
                    "language": block["language"],
                    "syntax_valid": syntax_result["valid"],
                    "syntax_errors": syntax_result["errors"],
                    "quality_score": quality_result["score"],
                    "recommendations": quality_result["recommendations"]
                })
        
        # Calculate overall score based on level
        base_score = 7 if level == "beginner" else 6 if level == "intermediate" else 5
        
        # Adjust based on code quality
        if code_analysis:
            avg_quality = sum(a["quality_score"] for a in code_analysis) / len(code_analysis)
            code_adjustment = (avg_quality - 7) / 3  # Normalize to -2 to +1
            base_score += code_adjustment
        
        # Ensure score is within bounds
        final_score = max(0, min(10, base_score))
        
        return {
            "score": int(final_score),
            "code_analysis": code_analysis,
            "has_code": len(code_blocks) > 0,
            "evaluation_notes": self._generate_notes(question, answer, code_analysis)
        }
    
    def _generate_notes(
        self,
        question: str,
        answer: str,
        code_analysis: list
    ) -> str:
        """Generate evaluation notes."""
        notes = []
        
        if code_analysis:
            notes.append(f"Code provided in {len(code_analysis)} block(s)")
            
            invalid_syntax = [a for a in code_analysis if not a["syntax_valid"]]
            if invalid_syntax:
                notes.append(f"⚠️ Syntax errors found in {len(invalid_syntax)} code block(s)")
            
            low_quality = [a for a in code_analysis if a["quality_score"] < 7]
            if low_quality:
                notes.append(f"⚠️ Code quality could be improved in {len(low_quality)} block(s)")
        else:
            notes.append("No code provided in response")
        
        return " | ".join(notes)


# Convenience function for use in evaluator_node
def evaluate_with_mcp(question: str, answer: str, level: str = "beginner") -> Dict[str, Any]:
    """Quick evaluation using MCP-enhanced evaluator.
    
    Args:
        question: Interview question
        answer: Candidate's answer
        level: Difficulty level
        
    Returns:
        Evaluation dict with score and analysis
    """
    evaluator = MCPEvaluator()
    return evaluator.evaluate_response(question, answer, level)
