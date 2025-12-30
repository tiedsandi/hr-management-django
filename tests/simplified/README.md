# Simplified Testing Approach

## Overview

Folder ini berisi contoh testing dengan pendekatan **simplified** sebagai perbandingan dengan folder `tests/api/` yang menggunakan **comprehensive approach** dengan factory pattern.

## Perbandingan

### Comprehensive Approach (`tests/api/`)
**Advantages:**
- ✅ Reusable data generation via factories
- ✅ Centralized fixtures di conftest.py
- ✅ DRY (Don't Repeat Yourself) - less code duplication
- ✅ Easy to maintain - ubah factory affects all tests
- ✅ Scalable for large projects

**Disadvantages:**
- ❌ Initial setup effort lebih besar
- ❌ Learning curve for factory-boy
- ❌ More abstraction layers

**Setup Time:** ~2-3 hours
**Files Created:** 10+ files (factories, fixtures, test files)

---

### Simplified Approach (`tests/simplified/`)
**Advantages:**
- ✅ Quick to start - no factory setup
- ✅ Easy to understand - direct object creation
- ✅ No additional libraries needed
- ✅ Good for small projects atau quick prototyping

**Disadvantages:**
- ❌ Code duplication across tests
- ❌ Harder to maintain - changes require updating multiple places
- ❌ Test data creation mixed with test logic
- ❌ Not scalable for large projects

**Setup Time:** ~30 minutes
**Files Created:** 1-2 test files

---

## When to Use Each Approach?

### Use Comprehensive Approach When:
- Project akan berkembang besar (10+ models)
- Team development (multiple developers)
- Butuh consistency dalam test data
- Long-term maintenance important
- CI/CD dengan coverage requirements

### Use Simplified Approach When:
- Small project (<5 models)
- Quick prototyping atau POC
- Solo developer dengan limited time
- Testing specific edge cases
- Learning Django/DRF testing basics

---

## Example Comparison

Lihat file-file di folder ini untuk contoh implementasi:
- `test_login_simple.py` - Basic login tests tanpa factory
- `test_profile_simple.py` - Basic profile tests tanpa factory

Bandingkan dengan:
- `tests/api/v1/accounts/test_login.py` - Menggunakan UserFactory
- `tests/api/v1/accounts/test_profile.py` - Menggunakan fixtures

---

## Recommendation

**Untuk project ini (HR Management System):**
- ✅ **Gunakan Comprehensive Approach**
- Alasan: Project akan berkembang dengan banyak models (Division, Employee, Attendance, Leave, dll)
- Initial effort sudah dilakukan, sekarang tinggal maintenance
- Return on investment: setup 3 jam = save 10+ jam di masa depan
