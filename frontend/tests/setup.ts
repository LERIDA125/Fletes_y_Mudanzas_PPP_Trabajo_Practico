import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// `globals: false` le impide a Testing Library registrar su cleanup solo; lo
// declaramos acá para que cada test arranque con un DOM limpio.
afterEach(cleanup);
