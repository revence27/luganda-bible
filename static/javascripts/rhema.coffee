$(() ->
  # workChapterNav()
  # workBookNav()
  newerBookNav()
  null
)

newerBookNav = () ->
  sel = $('#bnav')
  frm = $(sel.parent('form'))
  but = $($('input[type="submit"]', frm)[0])
  but.hide()
  sel.change((evt) ->
    document.location = "?book=#{$(this).val()}"
  )

workBookNav = () ->
  crb = $('#curbook')
  bnv = $('#bnav')
  bkn = $($('.bn', crb)[0])
  bkn.click((evt) ->
    dem = []
    for ent, ix in $('option', bnv)
      it  = $(ent)
      dem.push(
        text:     it.text()
        pos:      ix
        selected: it.attr('selected') == 'selected'
      )
      dem.push(it.text())
    inp = $('<input style="font: inherit" type="text" />')
    inp.attr('placeholder', bkn.text())
    inp.autocomplete({source: dem})
    bkn.before(inp)
    bkn.hide()
    # alert dem.join("\n")
  )
  bnv.parent('form').hide()

workChapterNav = () ->
  crb = $('#curbook')
  chd = $('#chapnav')
  chn = $($('.cn', crb)[0])
  chp = 0
  sld = chd.slider(
    range:  'min'
    min:    0
    max:    parseInt(chd.attr('chapter-count')) - 1
    value:  parseInt(chd.attr('active-chapter'))
    slide:  ((evt, ui) ->
      chp = ui.value
      chn.text(chp + 1)
    )
  )
  $('.chap', chd).hide()
  chn.click((evt) ->
    # alert(chp)
    document.location = "?book=#{chd.attr('active-book')}&chapter=#{chp}"
  )
