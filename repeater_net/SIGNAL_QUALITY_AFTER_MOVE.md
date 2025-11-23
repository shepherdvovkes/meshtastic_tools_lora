# Signal Quality Check - After bb14 Repositioning

**Date:** 2025-11-23  
**Action:** bb14 (REPEATER) was moved to a new position

## Current Visibility Status

### bb14 (REPEATER) - 192.168.0.15

**Can see:**
- ✅ **666c** (CLIENT) - Node ID: !9ee8666c
  - Channel Utilization: 0.0%
  - Air Util TX: 0.0%

**Cannot see:**
- ❌ **7284** (not visible in current query)
  - May need time for NodeInfo broadcast
  - May be out of range after move

**Status:** ⚠️ Can only see 666c currently

---

### 7284 (CLIENT) - 192.168.0.10

**Can see:**
- ✅ **bb14** (REPEATER) - Node ID: !9ee7bb14
  - Channel Utilization: 0.0%
  - Air Util TX: 0.0%

**Cannot see:**
- ❌ **666c** (not visible in current query)

**Status:** ✅ Can see bb14 repeater

---

### 666c (CLIENT) - 192.168.0.11

**Can see:**
- ✅ **7284** (CLIENT) - Node ID: !9ee87284
  - SNR: **11.75 dB** (excellent signal)
  - Channel Utilization: 0.1%
  - Air Util TX: 0.0%

- ✅ **bb14** (REPEATER) - Node ID: !9ee7bb14
  - SNR: **2.25 dB** (weak but usable)
  - Channel Utilization: 0.5%
  - Air Util TX: 0.0%

**Status:** ✅ Can see both 7284 and bb14

---

## Comparison: Before vs After Move

### Before Move (Previous Status)

| Link | SNR | Status |
|------|-----|--------|
| bb14 → 7284 | 0.75 dB | Weak |
| bb14 → 666c | Available | Visible |
| 7284 → bb14 | 10.75 dB | Good |
| 666c → bb14 | 2.25 dB | Weak |

### After Move (Current Status)

| Link | SNR | Status | Change |
|------|-----|--------|--------|
| bb14 → 7284 | **Not visible** | ❌ Lost | ⚠️ **Worse** |
| bb14 → 666c | Available | ✅ Visible | ➡️ Same |
| 7284 → bb14 | Available | ✅ Visible | ➡️ Same |
| 666c → bb14 | 2.25 dB | Weak | ➡️ Same |
| 666c → 7284 | 11.75 dB | Excellent | ➡️ Same |

## Analysis

### ⚠️ Issues After Move

1. **bb14 lost visibility to 7284:**
   - bb14 can no longer see 7284
   - This breaks the repeater chain: 7284 → bb14 → 666c
   - Messages from 7284 cannot route through bb14

2. **7284 cannot see 666c:**
   - Direct link may be broken
   - Relies on bb14 for routing, but bb14 can't see 7284

### ✅ Still Working

1. **666c has good connectivity:**
   - Can see both 7284 (11.75 dB) and bb14 (2.25 dB)
   - Best positioned node

2. **7284 can see bb14:**
   - Connection exists from 7284 → bb14
   - But bb14 cannot see 7284 (one-way visibility issue)

## Recommendations

### Immediate Actions

1. **Wait for NodeInfo broadcasts:**
   - Nodes broadcast NodeInfo every 3 hours (or when triggered)
   - Wait a few minutes and check again
   - Send a test message to trigger NodeInfo update

2. **Check physical placement:**
   - bb14 may be too far from 7284 now
   - Move bb14 closer to 7284
   - Ensure bb14 is between 7284 and 666c

3. **Test connectivity:**
   - Send test messages to trigger routing updates
   - Monitor if visibility improves

### Optimal Placement

For repeater network (7284 → bb14 → 666c):

```
[7284] ----(close)----> [bb14] ----(close)----> [666c]
```

- bb14 should be **equidistant** between 7284 and 666c
- bb14 should be **within range** of both clients
- All nodes should be able to see each other

## Next Steps

1. **Wait 2-3 minutes** for NodeInfo broadcasts
2. **Re-check visibility** from all nodes
3. **Send test messages** to trigger routing updates
4. **Adjust bb14 position** if visibility doesn't improve
5. **Monitor SNR values** to optimize placement

## Current Network Status

⚠️ **Partial connectivity:**
- ✅ 666c can see both 7284 and bb14
- ✅ 7284 can see bb14
- ❌ bb14 cannot see 7284 (critical for repeater function)
- ❌ 7284 cannot see 666c directly

**Repeater chain status:** ⚠️ **BROKEN** - bb14 cannot see 7284

**Action required:** Reposition bb14 or wait for NodeInfo updates

