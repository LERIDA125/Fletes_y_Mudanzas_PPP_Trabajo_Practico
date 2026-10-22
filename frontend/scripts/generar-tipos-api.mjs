import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import openapiTS, { astToString } from "openapi-typescript";

const directorioFrontend = dirname(dirname(fileURLToPath(import.meta.url)));
const raizRepositorio = resolve(directorioFrontend, "..");
const directorioBackend = join(raizRepositorio, "backend");

const contratoJson = join(directorioFrontend, "src", "types", "openapi.json");
const tiposSalida = join(directorioFrontend, "src", "types", "openapi.d.ts");

// El backend define su contrato en código Python, así que el único modo de obtenerlo sin
// levantar el servidor es importando la aplicación. Se resuelve el intérprete del entorno
// virtual del backend porque este script corre desde `frontend/` y no puede asumir que el
// entorno de Python está activo. `OPENAPI_PYTHON` permite sobreescribirlo.
function resolverPython() {
  if (process.env.OPENAPI_PYTHON) {
    return process.env.OPENAPI_PYTHON;
  }

  const candidatos = [
    join(directorioBackend, ".venv", "Scripts", "python.exe"),
    join(directorioBackend, ".venv", "bin", "python"),
  ];

  return candidatos.find(existe) ?? "python";
}

function existe(ruta) {
  return existsSync(ruta);
}

function exportarContrato() {
  const python = resolverPython();
  const resultado = spawnSync(python, ["-m", "scripts.exportar_openapi", contratoJson], {
    cwd: directorioBackend,
    stdio: ["ignore", "inherit", "inherit"],
  });

  if (resultado.error) {
    throw new Error(
      `No se pudo ejecutar ${python}: ${resultado.error.message}. ` +
        `Definí OPENAPI_PYTHON con el intérprete que tiene instalado el backend.`,
    );
  }

  if (resultado.status !== 0) {
    throw new Error(
      `El backend no pudo publicar su contrato OpenAPI (salida ${resultado.status}).`,
    );
  }
}

async function generarTipos() {
  const contrato = JSON.parse(readFileSync(contratoJson, "utf8"));
  const tipos = await openapiTS(contrato);
  writeFileSync(tiposSalida, `${astToString(tipos)}\n`, "utf8");
}

async function main() {
  try {
    exportarContrato();
    await generarTipos();
    console.log("Tipos generados en src/types/openapi.d.ts");
  } finally {
    if (existsSync(contratoJson)) {
      rmSync(contratoJson);
    }
  }
}

await main();
