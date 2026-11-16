// 사이트 전체에 비밀번호를 건다 (Vercel Routing Middleware).
// 비밀번호는 Vercel 환경 변수 SITE_PASSWORD 에 둔다. 아이디 칸은 아무 값이나 넣어도 된다.
export const config = { matcher: '/(.*)' };

export default function middleware(request) {
  const expected = process.env.SITE_PASSWORD;
  const header = request.headers.get('authorization') || '';

  if (expected && header.startsWith('Basic ')) {
    try {
      const decoded = new TextDecoder().decode(
        Uint8Array.from(atob(header.slice(6)), (c) => c.charCodeAt(0))
      );
      const password = decoded.slice(decoded.indexOf(':') + 1);
      if (password === expected) {
        return new Response(null, { headers: { 'x-middleware-next': '1' } });
      }
    } catch (e) {
      // 잘못된 헤더는 아래에서 다시 묻는다
    }
  }

  // 비밀번호가 설정되지 않았으면 아무도 들어오지 못하게 막는다.
  return new Response('비밀번호가 필요합니다.', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="SQL Lecture", charset="UTF-8"',
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store',
    },
  });
}
