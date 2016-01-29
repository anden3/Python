import os
import shutil

cc_dir = os.path.join("C:" + os.sep + "Users" + os.sep + "andre" + os.sep + "Downloads")
done_dir = os.path.join("C:" + os.sep + "Users" + os.sep + "andre" + os.sep + "Downloads" + os.sep + "Sims_CC" + os.sep + "Added")

package_dir = os.path.join("C:" + os.sep + "Users" + os.sep + "andre" + os.sep + "Documents" + os.sep + "Electronic Arts" + os.sep + "The Sims 3" + os.sep + "Mods" + os.sep + "Packages")
pack_dir = os.path.join("C:" + os.sep + "Users" + os.sep + "andre" + os.sep + "Documents" + os.sep + "Electronic Arts" + os.sep + "The Sims 3" + os.sep + "Downloads")

for subdir, dirs, files in os.walk(cc_dir):
    for file in files.copy():
        if file[file.rindex('.'):] == ".package":
            shutil.copy(file, package_dir)
            shutil.move(file, done_dir)
        elif file[file.rindex('.'):] == ".sims3pack":
            shutil.copy(file, pack_dir)
            shutil.move(file, done_dir)
