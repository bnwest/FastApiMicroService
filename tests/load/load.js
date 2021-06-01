import http from "k6/http";
import { check, group, sleep, fail } from "k6";
import { Rate } from 'k6/metrics';

import { uuidv4 } from "https://jslib.k6.io/k6-utils/1.0.0/index.js";

const fastapi_root = __ENV.FASTAPI_ROOT;
const fastapi_versions_url = fastapi_root + "/versions";

export default function() {
  group("GET", function() {
    let res = http.get(fastapi_versions_url);

    check(res, {
      "status is 200": r => r.status === 200,
    });

    let response_body = JSON.parse(res.body);

    let python_version   = response_body["python"];
    let fastapi_version  = response_body["fastapi"];
    let pydantic_version = response_body["pydantic"];
    let uvicorn_version  = response_body["uvicorn"];
  });
}
