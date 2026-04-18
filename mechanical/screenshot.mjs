#!/usr/bin/env node
// Screenshot assembly STEP via o3dv in headless Chromium
// Usage: node screenshot.mjs assembly-slim.step assembly-slim.png

import puppeteer from 'puppeteer';
import { createServer } from 'http';
import { readFileSync } from 'fs';
import { resolve, basename } from 'path';

const model = resolve(process.argv[2]);
const output = process.argv[3];
const modelName = basename(model);

const envBase = "https://cdn.jsdelivr.net/npm/online-3d-viewer@0.18.0/build/website/assets/envmaps/fishermans_bastion/";
const envMap = ["posx.jpg","negx.jpg","posy.jpg","negy.jpg","posz.jpg","negz.jpg"].map(f => envBase + f).join(",");

const html = `<!DOCTYPE html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/online-3d-viewer@0.18.0/build/engine/o3dv.min.js"></script>
<style>body{margin:0;overflow:hidden} .online_3d_viewer{width:2880px;height:1620px}</style>
</head><body>
<div class="online_3d_viewer" model="http://localhost:8765/${modelName}"
     edgesettings="on,40,40,40,1" backgroundcolor="255,255,255,255"
     environmentmap="${envMap}"></div>
<script>
window.addEventListener('load', function() {
    OV.Init3DViewerElements();
    setTimeout(function() { document.title = "ready"; }, 45000);
});
</script>
</body></html>`;

// Serve model file and HTML
const server = createServer((req, res) => {
    if (req.url === '/') {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.end(html);
    } else {
        const data = readFileSync(model);
        res.writeHead(200, {
            'Content-Type': 'application/octet-stream',
            'Access-Control-Allow-Origin': '*'
        });
        res.end(data);
    }
});
server.listen(8765);

const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'],
    defaultViewport: { width: 2880, height: 1620 },
});

const page = await browser.newPage();
await page.goto('http://localhost:8765/', { waitUntil: 'networkidle0' });
await page.waitForFunction(() => document.title === 'ready', { timeout: 60000 });
await new Promise(r => setTimeout(r, 3000));
await page.screenshot({ path: output, type: 'png' });
console.log(`Saved ${output}`);

await browser.close();
server.close();
