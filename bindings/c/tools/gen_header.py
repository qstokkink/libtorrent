#!/usr/bin/env python3

import pathlib

header = (
    pathlib.Path(__file__).parent / ".." / "include" / "libtorrent_settings.h"
).open("w+")
cpp = (pathlib.Path(__file__).parent / ".." / "src" / "settings.cpp").open("w+")

f = (
    pathlib.Path(__file__).parent
    / ".."
    / ".."
    / ".."
    / "include"
    / "libtorrent"
    / "settings_pack.hpp"
).open()

cpp.write(
    """// generated by tools/gen_header.py

#include <stdarg.h>
#include "libtorrent/settings_pack.hpp"

#include "libtorrent_settings.h"

int settings_key(int const tag)
{
	using sp = lt::settings_pack;
	switch (tag)
	{
"""  # noqa: E101,W191
)

header.write(
    """// generated by tools/gen_header.py

#ifndef LIBTORRENT_SETTINGS_H
#define LIBTORRENT_SETTINGS_H

// tags for session wide settings
enum settings_tags_t {
"""
)

in_block = False
in_define_block = False
first = True

for line in f:
    line = line.strip()

    if in_define_block:
        if line.startswith("#endif"):
            in_define_block = False
        continue

    if line == "{" or line == "" or line.startswith("//"):
        continue

    if in_block and line == "};":
        in_block = False
    elif line == "enum string_types":
        in_block = True
        arg_type = "char const*"
    elif line == "enum bool_types":
        in_block = True
        arg_type = "int (0 or 1)"
    elif line == "enum int_types":
        in_block = True
        arg_type = "int"
    elif not in_block:
        continue
    else:
        if line.startswith("#if"):
            in_define_block = True
            continue

        setting = line.replace(",", "").split("=")[0].strip()

        if setting.endswith("_internal"):
            continue

        cpp.write("		case SET_%s: return sp::%s;\n" % (setting.upper(), setting))
        if first:
            header.write("	SET_%s = 0x200, // %s\n" % (setting.upper(), arg_type))
            first = False
        else:
            header.write("	SET_%s, // %s\n" % (setting.upper(), arg_type))

cpp.write(
    """		default:
			// ignore unknown tags
			return -1;
	}
}

lt::settings_pack make_settings(int tag, va_list lp)
{
	lt::settings_pack ret;
	using sp = lt::settings_pack;
	while (tag != 0)
	{
		int const key = settings_key(tag);
		switch (key & lt::settings_pack::type_mask)
		{
			case sp::string_type_base:
				ret.set_str(key, va_arg(lp, char*));
				break;
			case sp::int_type_base:
				ret.set_int(key, va_arg(lp, int));
				break;
			case sp::bool_type_base:
				ret.set_bool(key, va_arg(lp, int));
				break;
		}
		tag = va_arg(lp, int);
	}
	return ret;
}

"""  # noqa: E101,W191
)

header.write(
    """};

#endif // LIBTORRENT_SETTINGS_H
"""
)
