# This file goes in ~ (same directory as .bashrc)
# If .bashrc does not contain similar lines, add following:
#  if [ -f ~/.bash_aliases ]; then
#      . ~/.bash_aliases
#  fi

# Standard cut/copy/paste
alias cp='cp -i'
alias rm='rm -i'
alias mv='mv -i'

# Grep through all c-source files
# Ex: grepirch joint_state .
alias grepirch='grep -irn --include=*.{c,cpp,h,hpp}'

# Catkin/Cmake shortcuts. catkin/cmake_eclipse generate eclipse project files.
# (obsolete) alias catkin_eclipse='catkin_make --force-cmake -G"Eclipse CDT4 - Unix Makefiles"'
alias catkin_eclipse='catkin_make --force-cmake -G"Eclipse CDT4 - Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_ECLIPSE_MAKE_ARGUMENTS=-j8'
alias catkin_nowarnings='catkin_make --cmake-args -DCMAKE_CXX_FLAGS="-w"'
alias cmake_eclipse='cmake -G"Eclipse CDT4 - Unix Makefiles" -D CMAKE_BUILD_TYPE=Debug'


