#!/bin/bash

# Kosha Python SDK Development Helper

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}Kosha Python SDK Development Helper${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./dev.sh <command>"
    echo ""
    echo -e "${YELLOW}Standard Commands:${NC}"
    echo -e "  ${GREEN}validate${NC}                Run full CI validation (mimics GitHub Actions)"
    echo -e "  ${GREEN}test${NC}                    Run smoke test"
    echo -e "  ${GREEN}lint${NC}                    Run linters (black, flake8)"
    echo -e "  ${GREEN}format${NC}                  Auto-format code with black and isort"
    echo -e "  ${GREEN}clean${NC}                   Clean cache and build artifacts"
    echo ""
    echo -e "${YELLOW}Package Commands:${NC}"
    echo -e "  ${GREEN}install${NC}                 Install package in editable mode"
    echo -e "  ${GREEN}build${NC}                   Build package distribution"
    echo -e "  ${GREEN}publish-test${NC}            Publish to TestPyPI"
    echo -e "  ${GREEN}publish${NC}                 Publish to PyPI"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./dev.sh validate                # Full CI validation"
    echo "  ./dev.sh test                    # Smoke test"
    echo "  ./dev.sh build                   # Build package"
}

# Validate (mimics GitHub Actions CI)
validate() {
    echo -e "${BLUE}Running CI Validation for Python SDK...${NC}"

    # Install package
    echo -e "${YELLOW}Step 1: Installing package...${NC}"
    pip install -e . || exit 1

    # Lint
    echo -e "\n${YELLOW}Step 2: Linting...${NC}"
    run_lint || exit 1

    # Smoke test
    echo -e "\n${YELLOW}Step 3: Smoke test...${NC}"
    run_test || exit 1

    echo -e "\n${GREEN}✅ Python SDK validation passed${NC}"
}

# Run smoke test
run_test() {
    echo -e "${BLUE}Running smoke test...${NC}"
    python -c "from kosha_client import KoshaClient; print('✅ Import successful')" || exit 1
    echo -e "${GREEN}✅ Smoke test passed${NC}"
}

# Run linting
run_lint() {
    echo -e "${BLUE}Running linters...${NC}"

    echo -e "${YELLOW}Running Black...${NC}"
    black --check kosha_client.py examples/ 2>/dev/null || {
        echo -e "${RED}❌ Black formatting issues found. Run './dev.sh format' to fix.${NC}"
        return 1
    }

    echo -e "${YELLOW}Running Flake8...${NC}"
    flake8 kosha_client.py examples/ --max-line-length=120 2>/dev/null || {
        echo -e "${RED}❌ Flake8 issues found.${NC}"
        return 1
    }

    echo -e "${GREEN}✅ Linting complete${NC}"
}

# Auto-format code
run_format() {
    echo -e "${BLUE}Formatting code...${NC}"

    black kosha_client.py examples/
    isort kosha_client.py examples/ 2>/dev/null || true

    echo -e "${GREEN}✅ Code formatted${NC}"
}

# Clean artifacts
clean() {
    echo -e "${BLUE}Cleaning artifacts...${NC}"

    rm -rf __pycache__ .pytest_cache .mypy_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true

    echo -e "${GREEN}✅ Cleaned${NC}"
}

# Install package
install_package() {
    echo -e "${BLUE}Installing package in editable mode...${NC}"
    pip install -e .
    pip install black flake8 build twine
    echo -e "${GREEN}✅ Installed${NC}"
}

# Build package
build_package() {
    echo -e "${BLUE}Building package...${NC}"
    pip install build
    python -m build
    echo -e "${GREEN}✅ Built: dist/${NC}"
    ls -lh dist/
}

# Publish to TestPyPI
publish_test() {
    echo -e "${BLUE}Publishing to TestPyPI...${NC}"
    build_package
    python -m twine upload --repository testpypi dist/*
    echo -e "${GREEN}✅ Published to TestPyPI${NC}"
}

# Publish to PyPI
publish() {
    echo -e "${YELLOW}⚠️  Publishing to PyPI (production)${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        build_package
        python -m twine upload dist/*
        echo -e "${GREEN}✅ Published to PyPI${NC}"
    else
        echo -e "${RED}Cancelled${NC}"
    fi
}

# Main command handler
case "${1:-help}" in
    validate)
        validate
        ;;
    test)
        run_test
        ;;
    lint)
        run_lint
        ;;
    format)
        run_format
        ;;
    clean)
        clean
        ;;
    install)
        install_package
        ;;
    build)
        build_package
        ;;
    publish-test)
        publish_test
        ;;
    publish)
        publish
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
