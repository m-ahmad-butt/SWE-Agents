from pydantic import BaseModel, Field

# pydantic (output parser)
#GeneratedFile(
#    path="frontend/src/pages/Login.tsx",
#    content="""
#export default function Login(){
#    return <h1>Login</h1>
#}
#""",
#    language="typescript"
#)
class GeneratedFile(BaseModel):
    path: str = Field(description="Relative path e.g. backend/routes/auth.py")
    content: str
    language: str = Field(description="python or typescript")


# pydantic (output parser) -> codewriter
# CodeBundle(
#    files=[
#        GeneratedFile(path="backend/routes/auth.py", content="", language="python"),
#        GeneratedFile(path="frontend/src/pages/Login.tsx", content="", language="typescript"),
#    ],
#    summary="Backend: wrote 1 file for auth, Frontend: wrote 1 file for Login"
# )
class CodeBundle(BaseModel):
    files: list[GeneratedFile]
    summary: str = ""
