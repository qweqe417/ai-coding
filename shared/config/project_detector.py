"""
项目类型检测器

自动检测项目类型、语言、框架和构建工具
"""

import os
import json
from typing import Dict, Any, List, Optional


class ProjectType:
    """项目类型数据类"""

    def __init__(
        self,
        category: str,
        language: str,
        framework: str,
        build_tool: str
    ):
        self.category = category  # backend | frontend | fullstack
        self.language = language  # java | python | go | nodejs | javascript
        self.framework = framework  # springboot | flask | vue3 | react | ...
        self.build_tool = build_tool  # maven | gradle | npm | yarn | pnpm

    def to_dict(self) -> Dict[str, str]:
        return {
            "category": self.category,
            "language": self.language,
            "framework": self.framework,
            "build_tool": self.build_tool
        }


class ProjectDetector:
    """项目类型检测器"""

    def __init__(self, project_root: str = "."):
        self.project_root = project_root

    def detect_project_type(self) -> ProjectType:
        """
        自动检测项目类型

        Returns:
            ProjectType: 项目类型信息
        """
        # 检测Java项目
        if os.path.exists(f"{self.project_root}/pom.xml"):
            return self._detect_java_project()

        # 检测Python项目
        if (os.path.exists(f"{self.project_root}/requirements.txt") or
            os.path.exists(f"{self.project_root}/pyproject.toml")):
            return self._detect_python_project()

        # 检测Go项目
        if os.path.exists(f"{self.project_root}/go.mod"):
            return self._detect_go_project()

        # 检测Node.js/前端项目
        if os.path.exists(f"{self.project_root}/package.json"):
            return self._detect_nodejs_project()

        # 默认返回未知类型
        return ProjectType("unknown", "unknown", "unknown", "unknown")

    def _detect_java_project(self) -> ProjectType:
        """检测Java项目类型"""
        # 读取pom.xml检测框架
        pom_path = f"{self.project_root}/pom.xml"
        with open(pom_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'spring-boot' in content:
            framework = "springboot"
        elif 'dubbo' in content:
            framework = "dubbo"
        else:
            framework = "java"

        # 检测构建工具
        if os.path.exists(f"{self.project_root}/build.gradle"):
            build_tool = "gradle"
        else:
            build_tool = "maven"

        return ProjectType("backend", "java", framework, build_tool)

    def _detect_python_project(self) -> ProjectType:
        """检测Python项目类型"""
        framework = "python"

        # 检测框架
        if os.path.exists(f"{self.project_root}/requirements.txt"):
            with open(f"{self.project_root}/requirements.txt", 'r') as f:
                content = f.read().lower()

                if 'flask' in content:
                    framework = "flask"
                elif 'django' in content:
                    framework = "django"
                elif 'fastapi' in content:
                    framework = "fastapi"

        return ProjectType("backend", "python", framework, "pip")

    def _detect_go_project(self) -> ProjectType:
        """检测Go项目类型"""
        framework = "go"

        # 读取go.mod检测框架
        if os.path.exists(f"{self.project_root}/go.mod"):
            with open(f"{self.project_root}/go.mod", 'r') as f:
                content = f.read()

                if 'gin-gonic/gin' in content:
                    framework = "gin"
                elif 'labstack/echo' in content:
                    framework = "echo"

        return ProjectType("backend", "go", framework, "go")

    def _detect_nodejs_project(self) -> ProjectType:
        """检测Node.js/前端项目类型"""
        package_json_path = f"{self.project_root}/package.json"

        with open(package_json_path, 'r', encoding='utf-8') as f:
            package = json.load(f)

        dependencies = package.get('dependencies', {})
        dev_dependencies = package.get('devDependencies', {})
        all_deps = {**dependencies, **dev_dependencies}

        # 检测前端框架
        if 'vue' in all_deps:
            version = all_deps['vue']
            framework = "vue3" if version.startswith('^3') or version.startswith('3.') else "vue2"
            build_tool = self._detect_package_manager()
            return ProjectType("frontend", "javascript", framework, build_tool)

        elif 'react' in all_deps:
            build_tool = self._detect_package_manager()
            return ProjectType("frontend", "javascript", "react", build_tool)

        elif 'next' in all_deps:
            build_tool = self._detect_package_manager()
            return ProjectType("fullstack", "javascript", "nextjs", build_tool)

        # 检测后端框架
        elif 'express' in all_deps:
            build_tool = self._detect_package_manager()
            return ProjectType("backend", "nodejs", "express", build_tool)

        elif 'koa' in all_deps:
            build_tool = self._detect_package_manager()
            return ProjectType("backend", "nodejs", "koa", build_tool)

        # 默认Node.js项目
        build_tool = self._detect_package_manager()
        return ProjectType("backend", "nodejs", "nodejs", build_tool)

    def _detect_package_manager(self) -> str:
        """检测Node.js包管理器"""
        if os.path.exists(f"{self.project_root}/pnpm-lock.yaml"):
            return "pnpm"
        elif os.path.exists(f"{self.project_root}/yarn.lock"):
            return "yarn"
        else:
            return "npm"

    def _find_config_files(self) -> List[str]:
        """查找配置文件"""
        config_files = []

        # Spring Boot配置文件
        possible_files = [
            'src/main/resources/application.yml',
            'src/main/resources/application.yaml',
            'src/main/resources/application.properties',
            'src/main/resources/application-dev.yml',
            'src/main/resources/bootstrap.yml',
            'src/main/resources/bootstrap.properties'
        ]

        for file in possible_files:
            full_path = f"{self.project_root}/{file}"
            if os.path.exists(full_path):
                config_files.append(full_path)

        return config_files
