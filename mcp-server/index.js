import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, "..");

const server = new Server(
  {
    name: "ssh-manager",
    version: "1.0.0",
  },
  {
    capabilities: {
      resources: {},
      tools: {},
    },
  }
);

server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "ssh://config/devices",
        name: "Managed Devices",
        description: "List of managed SSH devices",
        mimeType: "application/json",
      },
    ],
  };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  if (request.params.uri === "ssh://config/devices") {
    // Assuming there's a devices.json or similar, otherwise search for it
    const possiblePaths = ["devices.json", "config/devices.json"];
    for (const p of possiblePaths) {
        try {
            const content = await fs.readFile(path.join(PROJECT_ROOT, p), "utf-8");
            return {
                contents: [{ uri: request.params.uri, mimeType: "application/json", text: content }],
            };
        } catch {}
    }
    return { contents: [{ uri: request.params.uri, mimeType: "application/json", text: "[]" }] };
  }
  throw new Error(`Resource not found: \${request.params.uri}`);
});

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "ping_device",
        description: "Tests connectivity to a device.",
        inputSchema: {
          type: "object",
          properties: {
            host: {
              type: "string",
              description: "The hostname or IP address of the device.",
            },
          },
          required: ["host"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "ping_device") {
    const { host } = request.params.arguments;
    try {
      const { stdout } = await execAsync(`ping -n 1 \${host}`);
      return { content: [{ type: "text", text: stdout }] };
    } catch (error) {
      return { content: [{ type: "text", text: `Ping failed: \${error.message}` }] };
    }
  }
  throw new Error(`Tool not found: \${request.params.name}`);
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SSH Manager MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
