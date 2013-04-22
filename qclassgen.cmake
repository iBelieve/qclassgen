#find_program( CLASSGEN_EXECUTABLE classgen DOC "Class Generator" )
#if( NOT CLASSGEN_EXECUTABLE )
   #message( SEND_ERROR "Failed to find Class Generator." )
#endif( NOT CLASSGEN_EXECUTABLE )

set(CLASSGEN_EXECUTABLE ${CMAKE_CURRENT_LIST_DIR}/qclassgen.py)

# - Pass a list of files through the Qt Property Generator
#
# PROCESS( OUTVAR source1 ... sourceN )
#
#  OUTVAR  A list containing all the output souce file names, suitable
#          to be passed to add_executable or add_library.
#
# Example:
#  classgen(SRCS src/test1 src/test2)
function(QCLASSGEN OUTVAR)
   set( outfiles )
   foreach( f ${ARGN} )
     # first we might need to make the input file absolute
     get_filename_component( f "${f}" ABSOLUTE )
     file( RELATIVE_PATH rf "${CMAKE_CURRENT_SOURCE_DIR}" "${f}" )
     set(of "${CMAKE_CURRENT_BINARY_DIR}/${rf}")
     
     set(header_in  "${f}.h")
     set(header_out "${of}.h")
     set(source_in  "${f}.cpp")
     set(source_out "${of}.cpp")
     set(gen_f      "${of}.gen")
     set(moc_f      "${of}.moc")
     # create the output directory if it doesn't exist
     get_filename_component(in_dir "${f}" PATH)
     get_filename_component(out_dir "${of}" PATH)
     if( NOT IS_DIRECTORY "${out_dir}" )
         file( MAKE_DIRECTORY "${out_dir}" )
     endif( NOT IS_DIRECTORY "${out_dir}" )
     # now add the custom command to generate the output file
     add_custom_command(OUTPUT "${gen_f}" "${header_out}"
         COMMAND ${CLASSGEN_EXECUTABLE}
         ARGS "${header_in}" "${gen_f}" "${header_out}"
         DEPENDS "${heaer_in}" "${CLASSGEN_EXECUTABLE}"
         WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
       )
     add_custom_command(OUTPUT "${source_out}"
         COMMAND cp
         ARGS "${source_in}" "${source_out}"
         DEPENDS "${source_in}" "${header_out}"
       )
     qt4_generate_moc(${header_out} ${moc_f})
     # append the output file to the list of outputs
     list( APPEND outfiles "${source_out}" "${header_out}")
   endforeach(f)
   #qt4_automoc(${outfiles})
   # set the output list in the calling scope
   set(${OUTVAR} ${${OUTVAR}} ${outfiles} PARENT_SCOPE )
endfunction( QCLASSGEN )