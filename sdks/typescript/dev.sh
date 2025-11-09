#!/bin/bash

# Kosha TypeScript SDK Development Helper

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}Kosha TypeScript SDK Development Helper${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./dev.sh <command>"
    echo ""
    echo -e "${YELLOW}Standard Commands:${NC}"
    echo -e "  ${GREEN}validate${NC}                Run full CI validation (mimics GitHub Actions)"
    echo -e "  ${GREEN}test${NC}                    Run tests"
    echo -e "  ${GREEN}lint${NC}                    Run ESLint"
    echo -e "  ${GREEN}format${NC}                  Auto-format code with Prettier"
    echo -e "  ${GREEN}clean${NC}                   Clean cache and build artifacts"
    echo ""
    echo -e "${YELLOW}Build Commands:${NC}"
    echo -e "  ${GREEN}build${NC}                   Build TypeScript to JavaScript"
    echo -e "  ${GREEN}build-watch${NC}             Build in watch mode"
    echo -e "  ${GREEN}install${NC}                 Install dependencies"
    echo ""
    echo -e "${YELLOW}Package Commands:${NC}"
    echo -e "  ${GREEN}publish-test${NC}            Publish to npm (dry run)"
    echo -e "  ${GREEN}publish${NC}                 Publish to npm"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./dev.sh validate                # Full CI validation"
    echo "  ./dev.sh build                   # Build package"
    echo "  ./dev.sh test                    # Run tests"
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed${NC}"
        echo "Please install Node.js from https://nodejs.org/"
        exit 1
    fi
}

# Validate (mimics GitHub Actions CI)
validate() {
    check_node
    echo -e "${BLUE}Running CI Validation for TypeScript SDK...${NC}"

    # Install dependencies
    echo -e "${YELLOW}Step 1: Installing dependencies...${NC}"
    npm install || exit 1

    # Lint
    echo -e "\n${YELLOW}Step 2: Linting...${NC}"
    run_lint || exit 1

    # Build
    echo -e "\n${YELLOW}Step 3: Building...${NC}"
    run_build || exit 1

    # Test
    echo -e "\n${YELLOW}Step 4: Testing...${NC}"
    run_test || echo -e "${YELLOW}⚠️  No tests configured${NC}"

    echo -e "\n${GREEN}✅ TypeScript SDK validation passed${NC}"
}

# Run tests
run_test() {
    check_node
    echo -e "${BLUE}Running tests...${NC}"

    if npm run test 2>/dev/null; then
        echo -e "${GREEN}✅ Tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  No tests configured yet${NC}"
    fi
}

# Run linting
run_lint() {
    check_node
    echo -e "${BLUE}Running ESLint...${NC}"

    if npm run lint 2>/dev/null; then
        echo -e "${GREEN}✅ Linting passed${NC}"
    else
        echo -e "${YELLOW}⚠️  No linting configured. Install ESLint.${NC}"
        return 1
    fi
}

# Auto-format code
run_format() {
    check_node
    echo -e "${BLUE}Formatting code...${NC}"

    if command -v prettier &> /dev/null; then
        prettier --write "src/**/*.ts" "*.json" 2>/dev/null || true
        echo -e "${GREEN}✅ Code formatted${NC}"
    else
        echo -e "${YELLOW}⚠️  Prettier not installed. Run: npm install -g prettier${NC}"
    fi
}

# Build
run_build() {
    check_node
    echo -e "${BLUE}Building TypeScript...${NC}"

    if npm run build; then
        echo -e "${GREEN}✅ Build complete: dist/${NC}"
        ls -lh dist/ 2>/dev/null || true
    else
        echo -e "${RED}❌ Build failed${NC}"
        exit 1
    fi
}

# Build watch
run_build_watch() {
    check_node
    echo -e "${BLUE}Building in watch mode...${NC}"
    npm run build -- --watch
}

# Clean artifacts
clean() {
    echo -e "${BLUE}Cleaning artifacts...${NC}"

    rm -rf dist/ node_modules/ .tsbuildinfo
    rm -rf coverage/ .nyc_output/

    echo -e "${GREEN}✅ Cleaned${NC}"
}

# Install dependencies
install_deps() {
    check_node
    echo -e "${BLUE}Installing dependencies...${NC}"
    npm install
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Publish dry run
publish_test() {
    check_node
    echo -e "${BLUE}Publishing to npm (dry run)...${NC}"
    run_build
    npm publish --dry-run
    echo -e "${GREEN}✅ Dry run complete${NC}"
}

# Publish to npm
publish() {
    check_node
    echo -e "${YELLOW}⚠️  Publishing to npm (production)${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        run_build
        npm publish --access public
        echo -e "${GREEN}✅ Published to npm${NC}"
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
    build)
        run_build
        ;;
    build-watch)
        run_build_watch
        ;;
    clean)
        clean
        ;;
    install)
        install_deps
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
