# vscode-samples reasdme

A collection of sample applications demonstrating Visual Studio Code configuration and debugging features for Node.js applications, available in both JavaScript and TypeScript implementations.

## Project Highlights (important)

This repository contains two parallel implementations of a Node.js Express web application:
- **node-express-javascript**: JavaScript implementation
- **node-express-typescript**: TypeScript implementation

Both implementations showcase VS Code's debugging capabilities, task automation with Gulp, and proper project structure for Express applications.

## (important) Repository Structure from the top

```
.
├── node-express-javascript/     # JavaScript Express application
│   ├── bin/www                  # Server entry point
│   ├── app.js                   # Express application setup
│   ├── routes/                  # Route handlers
│   │   ├── index.js            # Home route
│   │   └── users.js            # Users route
│   ├── views/                   # Jade templates
│   ├── public/                  # Static assets
│   ├── tests/                   # Mocha test suite
│   ├── gulpfile.js             # Build automation
│   └── .vscode/                # VS Code configuration
├── node-express-typescript/     # TypeScript Express application
│   ├── src/
│   │   ├── www.ts              # Server entry point
│   │   ├── app.ts              # Express application setup
│   │   └── routes/             # Route handlers
│   ├── out/                    # Compiled JavaScript output
│   ├── tests/                  # TypeScript test suite
│   ├── gulpfile.js             # Build automation
│   └── .vscode/                # VS Code configuration
├── .claude/                     # Claude Code custom commands
│   └── commands/
│       └── monitor-pr.md       # PR monitoring command
├── monitor_script.sh            # GitHub PR monitoring script
└── README.md                    # Quick start guide
```

## Important Components

### JavaScript Application (node-express-javascript)

**Main Application** (`app.js`)
- Express 4.x web server setup
- Middleware configuration (morgan logger, body-parser, cookie-parser)
- Jade templating engine
- Environment-aware error handling (development vs production)
- 404 error handling

**Server Entry Point** (`bin/www`)
- HTTP server creation and configuration
- Port normalization from environment variables (default: 3000)
- Error handling for EACCES and EADDRINUSE
- Server event listeners

**Routes Info**
- `/` - Home page (routes/index.js:17) - renders "Visual Studio Code!" title
- `/users` - Users endpoint (routes/users.js:5) - returns placeholder response

**Build System** (`gulpfile.js`)
- `gulp watch` - Monitors LESS file changes
- `gulp less` - Compiles LESS to CSS
- `gulp test` - Runs Mocha test suite
- `gulp nodemon` - Auto-restarts server on file changes
- `gulp browser-sync` - Live browser reloading with proxy on port 7000
- `gulp default` - Runs browser-sync with nodemon and watch

**Dependencies**
- express: Web framework
- jade: Template engine
- morgan: HTTP request logger
- body-parser: Request body parsing middleware
- cookie-parser: Cookie parsing middleware
- serve-favicon: Favicon serving

**Dev Dependencies**
- gulp, gulp-less, gulp-mocha, gulp-nodemon: Build automation
- browser-sync: Live reloading
- mocha: Testing framework

### TypeScript Application (node-express-typescript)

**Main Application** (`src/app.ts`)
- TypeScript-based Express application
- Identical functionality to JavaScript version
- Strong typing with @types packages
- ES6 module imports

**Server Entry Point (imp)** (`src/www.ts`)
- Type-safe server initialization
- Typed function signatures for normalizePort, onError, onListening
- Identical functionality to JavaScript version

**Build System Specs**
- TypeScript compilation via `npm run compile`
- Separate tsconfig.json for source and tests
- Output directory: `./out/`

**Additional Dev Dependencies**
- typescript: TypeScript compiler
- @types/*: Type definitions for all dependencies
- gulp-tsb: TypeScript compilation for Gulp

### VS Code Configuration

Both projects include comprehensive VS Code settings in `.vscode/`:

**Launch Configurations** (`.vscode/launch.json`)
1. **Launch Program**: Runs the application with debugger
   - JavaScript: `bin/www`
   - TypeScript: `out/www.js`
2. **Attach to Port**: Attaches debugger to port 5858
3. **Mocha Tests**: Runs test suite with debugger

**Tasks** (`.vscode/tasks.json`)
- Build tasks for compilation
- Test runner integration

### Testing

**JavaScript Tests** (`tests/test.js`)
- Simple Mocha test suite
- Tests Array.indexOf() functionality
- Run with: `npm test` or `gulp test`

**TypeScript Tests** (`tests/test.ts`)
- TypeScript version of test suite
- Requires compilation before running

### Additional Tools (less important)

**PR Monitoring Script** (`monitor_script.sh`)
- Monitors GitHub PR comments for 48 hours
- Fetches comments and reviews every hour using `gh` CLI
- Tracks PR #1 in gshubham55/terminal-ide repository
- Parses JSON responses with `jq`
- Logs comment counts and content

**Claude Code Command** (`.claude/commands/monitor-pr.md`)
- Custom slash command for automated PR monitoring
- Monitors PRs continuously for 48 hours (1-hour intervals)
- Automatically resolves PR comments by:
  - Fetching comments via GitHub CLI
  - Analyzing requested changes
  - Implementing code modifications
  - Running tests
  - Replying to comments when resolved

## Getting Started

### Prerequisites

```bash
npm install -g gulp
```

### JavaScript Version

```bash
cd node-express-javascript
npm install
code .
```

Press `F5` to start debugging, then visit http://localhost:3000

### TypeScript Version

```bash
cd node-express-typescript
npm install
npm run compile
code .
```

Press `F5` to start debugging, then visit http://localhost:3000

### Development Workflow

**For JavaScript:**
```bash
gulp                 # Start browser-sync + nodemon + watch
gulp test           # Run tests
```

**For TypeScript:**
```bash
npm run compile      # Compile TypeScript
npm run compiletests # Compile tests
npm test            # Run compiled tests
gulp                # Start browser-sync + watch
```

## Key Files Reference

| File | Purpose | Location |
|------|---------|----------|
| Main app config | Express setup, middleware, error handling | `app.js` / `src/app.ts` |
| Server startup | HTTP server creation, port config | `bin/www` / `src/www.ts` |
| Home route | GET / endpoint | `routes/index.js:17` / `src/routes/index.ts` |
| Build automation | Gulp tasks for LESS, tests, live reload | `gulpfile.js` |
| Debug config | VS Code launch configurations | `.vscode/launch.json` |
| Tests | Mocha test suite | `tests/test.js` / `tests/test.ts` |

## All Environment Variables

- `PORT`: Server port (default: 3000)
- `NODE_ENV`: Environment mode ('development' or 'production')

## VS Code Workspace Settings

Located in `.vscode/settings.json`:
- Font: Fira Code, 16px
- Theme: Dark+
- Word wrap enabled
- Minimap disabled
- Auto-save enabled
- Persistent terminal sessions

## License

MIT License - See LICENSE file for details

## Third-Party Notices

See thirdpartynotices.txt for dependency licenses and attributions.
