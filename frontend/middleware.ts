/**
 * Next.js middleware — reads the language cookie and exposes it as
 * a response header so server components can read it without
 * importing js-cookie (which is client-only).
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const lang = request.cookies.get("lexindia_lang")?.value || "english";
  const response = NextResponse.next();
  response.headers.set("x-language", lang);
  return response;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
