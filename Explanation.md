# Explanation of Bug Fix

## What was the bug?
The test `test_header_not_added_for_dict_token` was failing because the `Client.request()` method incorrectly added an `Authorization` header even when `oauth2_token` was a simple dictionary. In the original code, any non-`OAuth2Token` value—including a dictionary—triggered the `refresh_oauth2()` method. This method replaced the dictionary with a valid `OAuth2Token`, which always included the `as_header()` method. As a result, an `Authorization` header was automatically added, violating the test’s expectation that no header should be present for dictionary tokens.

---

## Why did it happen?
The issue arose due to insufficient type checking of the `oauth2_token`. The code only verified whether the token existed and if it was expired, without differentiating between valid `OAuth2Token` objects and other types such as dictionaries:

```python
if not self.oauth2_token or not isinstance(self.oauth2_token, OAuth2Token) or self.oauth2_token.expired:
    self.refresh_oauth2()

if hasattr(self.oauth2_token, "as_header"):
    headers["Authorization"] = self.oauth2_token.as_header()
```

Because dictionaries triggered a refresh, the subsequent header addition always occurred, causing the test failure.

## Why does your fix solve it?

The fix explicitly ensures that only instances of OAuth2Token are checked for expiration and used to generate an Authorization header:

```python
if api and isinstance(self.oauth2_token, OAuth2Token):
    if self.oauth2_token.expired:
        self.refresh_oauth2()
    headers["Authorization"] = self.oauth2_token.as_header()
```

This prevents refresh_oauth2() from running on non-token types and ensures headers are only added when appropriate. After this fix, tests like test_header_not_added_for_dict_token pass, while valid tokens continue to function correctly.

## One realistic edge case your tests don’t cover

An OAuth2Token that expires exactly at the time of request may or may not trigger a refresh depending on timing precision, potentially causing intermittent issues. This precise timing scenario is not currently tested in the suite.