# Home Budget Web — Frontend (Variant A)

## Tests
The frontend uses **Vitest** for minimal logic tests.

## Run Tests
```
npm test
```

## Test Types

- **Unit tests**  
  Pure JavaScript logic (no DOM), located in:
  `src/tests/`

- **E2E smoke tests**  
  Currently **skipped by default**.  
  Enable manually by setting:
  ```
  BACKEND_URL=http://localhost:8000 npm test
  ```

## Notes
- No component rendering tests during Variant A.
- Avoid introducing UI-level coupling in tests.
- Keep diffs minimal.
