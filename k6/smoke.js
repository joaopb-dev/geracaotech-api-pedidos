import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 1,
  duration: '10s',
  thresholds: { checks: ['rate==1'], http_req_failed: ['rate==0'] },
};

export default function () {
  const response = http.post(`${__ENV.BASE_URL || 'http://localhost:8080'}/orders`,
    JSON.stringify({ items: [{ name: 'Livro', quantity: 2, unit_price_cents: 1250 }] }),
    { headers: { 'Content-Type': 'application/json' } });
  check(response, { 'pedido criado': (r) => r.status === 201,
    'total correto': (r) => r.json('total_cents') === 2500 });
}
