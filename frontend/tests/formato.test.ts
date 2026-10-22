import { describe, expect, it } from "vitest";

import {
  fechaCorta,
  primeraFilaDeLaPagina,
  totalPaginas,
  ultimaFilaDeLaPagina,
} from "@/lib/utils/formato";

describe("totalPaginas", () => {
  it("da 0 cuando no hay filas", () => {
    expect(totalPaginas(0, 20)).toBe(0);
  });

  it("da 1 cuando el total entra en una sola página", () => {
    expect(totalPaginas(1, 20)).toBe(1);
    expect(totalPaginas(20, 20)).toBe(1);
  });

  it("redondea hacia arriba cuando sobran filas", () => {
    expect(totalPaginas(21, 20)).toBe(2);
    expect(totalPaginas(45, 20)).toBe(3);
  });

  it("no divide por cero cuando el tamaño es inválido", () => {
    expect(totalPaginas(45, 0)).toBe(0);
    expect(totalPaginas(45, -5)).toBe(0);
  });
});

describe("primeraFilaDeLaPagina", () => {
  it("empieza en 1 en la primera página", () => {
    expect(primeraFilaDeLaPagina(1, 20)).toBe(1);
  });

  it("desplaza el inicio en las páginas siguientes", () => {
    expect(primeraFilaDeLaPagina(2, 20)).toBe(21);
    expect(primeraFilaDeLaPagina(3, 20)).toBe(41);
  });
});

describe("ultimaFilaDeLaPagina", () => {
  it("no se pasa del total en la última página", () => {
    expect(ultimaFilaDeLaPagina(1, 20, 45)).toBe(20);
    expect(ultimaFilaDeLaPagina(2, 20, 45)).toBe(40);
    expect(ultimaFilaDeLaPagina(3, 20, 45)).toBe(45);
  });
});

describe("fechaCorta", () => {
  it("formatea en el huso horario del negocio, no el del servidor", () => {
    // 2026-03-12T02:30:00Z = 2026-03-11 23:30 en Buenos Aires (UTC-3):
    // el día cambia, y solo se ve si el formateo usa la zona del negocio.
    expect(fechaCorta("2026-03-12T02:30:00Z")).toBe("11/03/2026");
  });

  it("devuelve un guion largo cuando la fecha no es interpretable", () => {
    expect(fechaCorta("no-es-una-fecha")).toBe("—");
  });
});
