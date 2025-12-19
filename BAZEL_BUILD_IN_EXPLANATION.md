# Why No BUILD.in Files?

## Short Answer

**BUILD.in files are not a standard Bazel feature.** Bazel uses `BUILD` or `BUILD.bazel` files directly - no template files are needed.

## Understanding BUILD vs BUILD.in

### Standard Bazel Approach

In Bazel, you write BUILD files directly:
- `BUILD` - Standard build configuration file
- `BUILD.bazel` - Alternative name (preferred in some contexts)

These are **not templates** - they are the actual configuration files that Bazel reads.

### What BUILD.in Would Be (If It Existed)

BUILD.in files would only make sense if:
1. They were templates that needed to be processed/generated
2. They contained variables that needed substitution
3. They were part of a custom build system on top of Bazel

But **this is not how Bazel works**. Bazel reads BUILD files directly.

## Confusion with Other Systems

You might be thinking of:

### 1. Python's MANIFEST.in
```
MANIFEST.in - Used by setuptools to specify which files to include in Python packages
```

But this is for Python packaging, not Bazel.

### 2. Template Files (.in extension)
```
some_template.in -> processed -> some_file
```

Some build systems use `.in` files as templates, but Bazel doesn't use this pattern.

### 3. CMake's CMakeLists.txt.in
CMake uses `.in` template files for configure_file(), but Bazel doesn't work this way.

## Our Project Structure

We have:
```
./BUILD                              ✅ Standard Bazel file
./common/BUILD                       ✅ Standard Bazel file
./services/taskprocessing/BUILD      ✅ Standard Bazel file
... (all BUILD files are standard)
```

**No BUILD.in files are needed** because:
1. We write BUILD files directly
2. Bazel reads them as-is
3. No template processing is required

## When You Might See BUILD.in

The only scenarios where you might encounter BUILD.in files:

1. **Custom tooling** - Some projects have custom scripts that generate BUILD files from templates
2. **Migration tools** - Tools that convert other build systems to Bazel might use templates
3. **Code generation** - If BUILD files are auto-generated from other sources

But for standard Bazel projects, you write BUILD files directly.

## Our Current Setup

Our BUILD files are:
- ✅ Direct Bazel configuration files
- ✅ No templates needed
- ✅ Standard Bazel approach

If we needed generated BUILD files, we would use:
- Bazel's native code generation (genrule, genquery, etc.)
- Starlark macros/functions
- Custom rules

But we don't need any of that - our BUILD files are straightforward and don't require templates.

## Conclusion

**No BUILD.in files exist because they're not part of Bazel's standard workflow.** We use BUILD files directly, which is the correct and standard approach for Bazel projects.

