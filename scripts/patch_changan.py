import os, re
PKG = "common/src/main/java/com/shilapi/xcertplay"

def ai(f):
    if not os.path.isfile(f): return
    with open(f) as fh: c = fh.read()
    if "BrandDetector" in c: return
    with open(f, "w") as fh: fh.write(c.replace("package com.shilapi.xcertplay", "package com.shilapi.xcertplay\n\nimport com.shilapi.xcertplay.BrandDetector", 1))

def gs(f):
    if not os.path.isfile(f): return
    ai(f)
    with open(f) as fh: c = fh.read()
    if "BrandDetector.isBydHeadUnit" in c: return
    m = re.search(r'(fun supported\([^)]*\)\s*:\s*Boolean\s*=\s*\{)', c)
    if m:
        c = c[:m.end()] + '\n        if (!BrandDetector.isBydHeadUnit()) return false\n' + c[m.end():]
        with open(f, "w") as fh: fh.write(c)
        return
    m = re.search(r'(fun supported\([^)]*\)\s*:\s*Boolean\s*=\s*)(\S)', c)
    if m:
        expr = c[m.start(2):].split("\n")[0].strip()
        new = f'fun supported(fingerprint: String = Build.FINGERPRINT): Boolean {{\n        if (!BrandDetector.isBydHeadUnit()) return false\n        return {expr}\n    }}'
        c = c[:m.start(1)] + new + c[m.end(2)+len(expr):]
        with open(f, "w") as fh: fh.write(c)
        print(f"  Patched {os.path.basename(f)}")

f = f"{PKG}/ClusterMapPresentation.kt"
if os.path.isfile(f):
    ai(f)
    with open(f) as fh: c = fh.read()
    t = "override fun onCreate(savedInstanceState: Bundle?)"
    if t in c and "BrandDetector.isBydHeadUnit" not in c:
        i = c.index(t) + len(t)
        c = c[:i] + "\n        if (!BrandDetector.isBydHeadUnit()) { finish(); return }\n" + c[i:]
        with open(f, "w") as fh: fh.write(c)
        print("  Patched ClusterMapPresentation.kt")

for n in ["DiLink51ClusterLayout.kt", "DiLink4ClusterDisplay.kt", "BydVehicleSettingsBackend.kt"]:
    gs(f"{PKG}/{n}")

ai(f"{PKG}/DiLink51ClusterMonitor.kt")
print("  Patched DiLink51ClusterMonitor.kt")

m = "common/src/main/AndroidManifest.xml"
if os.path.isfile(m):
    with open(m) as fh: c = fh.read()
    c = re.sub(r'(<intent-filter>\s*<action\s+android:name="android\.hardware\.usb\.action\.USB_DEVICE_ATTACHED"\s*/>\s*</intent-filter>)', '<!-- \\1 -->', c, flags=re.DOTALL)
    c = re.sub(r'(<meta-data\s+android:name="android\.hardware\.usb\.action\.USB_DEVICE_ATTACHED"[^/]*/\s*>)', '<!-- \\1 -->', c, flags=re.DOTALL)
    with open(m, "w") as fh: fh.write(c)
    print("  Patched AndroidManifest.xml")

# Create BrandDetector.kt

bi = f"{PKG}/BrandDetector.kt"
with open(bi, "w") as fh:
    fh.write('''package com.shilapi.xcertplay

import android.os.Build
import android.util.Log

object BrandDetector {
    private const val TAG = "BrandDetector"
    private var cached: Boolean? = null

    fun isBydHeadUnit(): Boolean {
        cached?.let { return it }
        val fp = Build.FINGERPRINT ?: ""
        val mfr = Build.MANUFACTURER ?: ""
        val r = fp.contains("BYD", true) || fp.contains("xdja", true) ||
                fp.contains("containerservice", true) || mfr.contains("BYD", true)
        Log.i(TAG, "isBYD=$r fp=$fp mfr=$mfr")
        cached = r
        return r
    }
}
''')
print("  Created BrandDetector.kt")
print("\nAll Changan UNI-T patches applied!")
