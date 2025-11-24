import { describe, it, expect } from "vitest";
import { formatNumber } from "../utils/formatNumber";

describe("formatNumber", () => {
  it("formats numbers to two decimals", () => {
    expect(formatNumber(5)).toBe("5.00");
    expect(formatNumber(3.1)).toBe("3.10");
    expect(formatNumber("7.456")).toBe("7.46");
  });

  it("returns null for invalid numbers", () => {
    expect(formatNumber("abc")).toBeNull();
    expect(formatNumber(undefined)).toBeNull();
  });
});
